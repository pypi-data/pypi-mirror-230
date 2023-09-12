from re import findall
from traceback import print_exc
from copy import deepcopy as copy
from json import dumps as json_dumps
from dacite import from_dict
from gitlab_ps_utils.misc_utils import safe_json_response, is_error_message_present
from gitlab_ps_utils.dict_utils import dig
from gitlab_evaluate.lib import utils, limits
from gitlab_evaluate.lib.flag_remediation import FlagRemediationMessages
from gitlab_evaluate.lib.api_models.user import User

class EvaluateApi():

    app_api_url = "/application/statistics"
    app_ver_url = "/version"
    
    def __init__(self, gitlab_api):
        self.gitlab_api = gitlab_api

    # Project only keyset-based pagination - https://docs.gitlab.com/ee/api/#keyset-based-pagination

    def get_last_id(self, link):
        # Get id_after value. If the Link key is missing it's done, with an empty list response
        return findall(r"id_after=(.+?)&", link)[0] if link else None

    '''
    Generates the URL to get the full project info with statistics
    '''
    def proj_info_get(self, i, source):
        '''Trying to create proper api call with project id.'''
        return f"{source}/api/v4/projects/{str(i)}?statistics=true"

    def proj_packages_url(self, i):
        return f"projects/{str(i)}/packages"

    def proj_registries_url(self, i):
        return f"projects/{str(i)}/registry/repositories"

    def proj_registries_tags_url(self, pid, rid):
        return f"projects/{str(pid)}/registry/repositories/{str(rid)}/tags"

    def proj_registries_tag_details_url(self, pid, rid, tid):
        return f"projects/{str(pid)}/registry/repositories/{str(rid)}/tags/{tid}"

    def get_registry_details(self, i):
        return f"registry/repositories/{str(i)}?size=true"

    ### Functions - Return API Data
    # Gets the X-Total from the statistics page with the -I on a curl
    def check_x_total_value_update_dict(self, check_func, p, host, token, api, value_column_name="DEFAULT_VALUE", over_column_name="DEFAULT_COLUMN_NAME", results={}):
        flag = False
        count = self.get_total_count(host, token, api, p['path_with_namespace'], value_column_name)
        if count is not None:
            num_over = check_func(count)
            if num_over:
                flag = True
            results[value_column_name] = count
            results[over_column_name] = num_over
        else:
            print(f"Could not retrieve {value_column_name} for project: {p.get('id')} - {p.get('path_with_namespace')}")
        return flag

    def get_total_count(self, host, token, api, full_path, entity):
        if count := self.gitlab_api.get_count(host, token, api):
            return count
        else:
            formatted_entity = utils.to_camel_case(entity)
            query = {
                "query": """
                    query {
                        project(fullPath: "%s") {
                            name,
                            %s {
                                count
                            }
                        }
                    }
                """ % (full_path, formatted_entity)
            }

            if gql_resp := safe_json_response(self.gitlab_api.generate_post_request(host, token, None, json_dumps(query), graphql_query=True)):
                return dig(gql_resp, 'data', 'project', formatted_entity, 'count')


    # gets the full stats of the project and sorts based on the returned items, passing a few through the HumanReadable utility
    def check_full_stats(self, url, project, my_dict, headers={}):
        if result := safe_json_response(self.gitlab_api.generate_get_request(host="", api="", token=headers.get("PRIVATE-TOKEN"), url=url)):
            my_dict.update({"last_activity_at": result.get("last_activity_at")})
            if kind := result.get("namespace"):
                my_dict.update({"kind": kind.get("kind")})
            if stats := result.get("statistics"):
                export_total = 0
                for k, v in stats.items():
                    updated_dict_entry = { k: v, k + "_over": utils.check_size(k, v)}
                    my_dict.update(updated_dict_entry)

                    # If k an item that would be part of the export, add to running total
                    if k in [
                        "repository_size",
                        "wiki_size",
                        "lfs_objects_size",
                        "snippets_size",
                        "uploads_size"
                    ]:
                        export_total += int(v)

                # Write running total to my_dict
                my_dict.update({"Estimated Export Size": export_total})
                export_total = 0
                # reset running total? Not loop, so maybe not
            else:
                print(f"Could not extracts stats for project {project.get('path_with_namepsace')}.\n")
        else:
            print(f"Could not retrieve project with stats for project id: {project.get('id')}")

    def get_registry_size(self, pid, path_with_namespace, source, token):
        """
            Iterates over a project's registry data and returns the total size of registry data
        """
        if total_size := self.get_registry_size_by_graphql(path_with_namespace, source, token):
            print('Retrieved registry size by single GraphQL query')
        else:
            print('Warning: Unable to receive registry size by GraphQL queries. Falling back to REST calls')
            registry_hashes = {}
            for registry_repo in self.gitlab_api.list_all(source, token, self.proj_registries_url(pid)):
                error, _ = is_error_message_present(registry_repo)
                if error:
                    print(f'Container registry from {path_with_namespace} inaccessible or disabled. Skipping')
                    continue
                rid = registry_repo['id']
                for registry_tags in self.gitlab_api.list_all(source, token, self.proj_registries_tags_url(pid, rid)):
                    tid = registry_tags['name']
                    repo_details = safe_json_response(self.gitlab_api.generate_get_request(source, token, self.proj_registries_tag_details_url(pid, rid, tid)))
                    if repo_size := repo_details.get('total_size'):
                        registry_hashes['short_revision'] = repo_size

            total_size = sum(registry_hashes.values())

        return utils.sizeof_fmt(total_size), utils.check_storage_size(total_size)

    def get_registry_size_by_graphql(self, path_with_namespace, source, token):
        """
            Makes a single GraphQL query to get the total registry size
            of a project. This query could return an error stating
            the query result is too large
        """
        query = {
            'query': """
                query {
                    project(fullPath: "%s") {
                        statistics {
                            containerRegistrySize
                            }
                        }
                    }

            """ % path_with_namespace
        }
        if gql_resp := safe_json_response(self.gitlab_api.generate_post_request(source, token, None, data=json_dumps(query), graphql_query=True)):
            return dig(gql_resp, 'data', 'project', 'statistics', 'containerRegistrySize')
        return None

    def genericGet(self, host, token, api):
        return safe_json_response(self.gitlab_api.generate_get_request(host=host, token=token, api=api))
        
    def getApplicationInfo(self, host, token):
        return self.genericGet(host, token, self.app_api_url)

    def getVersion(self, host, token):
        return self.genericGet(host, token, self.app_ver_url)

    def getArchivedProjectCount(self, host, token):
        if resp := self.gitlab_api.generate_get_request(host=host,token=token,api='projects?archived=True'):
            result = resp.headers.get('X-Total')
            return result
        
    def build_initial_results(self, project):
        return {
            'Project': project.get('name'),
            'ID': project.get('id'),
            'archived': project.get('archived'),
            'last_activity_at': project.get('last_activity_at'),
            'URL': project.get('web_url'),
            'namespace': dig(project, 'namespace', 'full_path')
        }
        
    def get_all_project_data(self, host, token, p):
        results = self.build_initial_results(p)
        flags = []
        pid = p.get('id')
        statistics = p.get('statistics')
        # if self.output_to_screen:
        #     print('+' * 40)
        #     print(f"Name: {p.get('name')} ID: {pid}")
        #     print(f"Desc: {p.get('description')}")
        #     print(f"Archived: {p.get('archived')}")
        headers = {
            'PRIVATE-TOKEN': token
        }

        # Get the full project info with stats
        messages = FlagRemediationMessages(p.get('name'))
        full_stats_url = self.proj_info_get(pid, host)

        self.check_full_stats(
            full_stats_url,
            p,
            results,
            headers=headers
        )

        try:
            pipeline_endpoint = f"pipelines/{pid}"
            flags.append(self.handle_check(
                messages,
                self.check_x_total_value_update_dict(
                    utils.check_num_pl, p, host, token, pipeline_endpoint, "Pipelines", "Pipelines_over", results),
                "pipelines",
                limits.PIPELINES_COUNT))

            # Get number of issues per project
            issues_endpoint = f"projects/{pid}/issues"
            flags.append(self.handle_check(
                messages,
                self.check_x_total_value_update_dict(
                    utils.check_num_issues, p, host, token, issues_endpoint, "Issues", "Issues_over", results),
                "issues",
                limits.ISSUES_COUNT))

            # Get number of branches per project
            branches_endpoint = f"projects/{pid}/repository/branches"
            flags.append(self.handle_check(
                messages,
                self.check_x_total_value_update_dict(
                    utils.check_num_br, p, host, token, branches_endpoint, "Branches", "Branches_over", results),
                "branches",
                limits.BRANCHES_COUNT))

            # Get number of merge requests per project
            mrequests_endpoint = f"projects/{pid}/merge_requests"
            flags.append(self.handle_check(
                messages,
                self.check_x_total_value_update_dict(
                    utils.check_num_mr, p, host, token, mrequests_endpoint, "Merge Requests", "Merge Requests_over", results),
                "merge_requests",
                limits.MERGE_REQUESTS_COUNT))

            # Get number of tags per project
            tags_endpoint = f"projects/{pid}/repository/tags"
            flags.append(self.handle_check(
                messages,
                self.check_x_total_value_update_dict(
                    utils.check_num_tags, p, host, token, tags_endpoint, "Tags", "Tags_over", results),
                "tags",
                limits.TAGS_COUNT))

            # Get list of package types
            if p.get('packages_enabled', False):
                packages_in_use = set()
                for p in self.gitlab_api.list_all(host, token, self.proj_packages_url(pid)):
                    if isinstance(p, str):
                        print( f"failed to get project {pid} packages; expected dict got str; '{p}'")
                    else:
                        packages_in_use.add(p.get("package_type", ""))

                results['Package Types In Use'] = ", ".join(
                    packages_in_use) if packages_in_use else "N/A"
                if packages_in_use:
                    flags.append(True)
                    self.handle_check(messages, True, "packages",
                                    copy(results['Package Types In Use']))

            # Get total packages size
            # TODO: GET single project statistics when listing group projects
            if statistics:
                results['Total Packages Size'] = utils.sizeof_fmt(
                    statistics.get("packages_size", 0))

            # Get container registry size
            results['Container Registry Size'], flag_registries = self.get_registry_size(
                pid, p['path_with_namespace'], host, token)
            self.handle_check(messages, flag_registries, 'container_registries',
                              utils.sizeof_fmt(limits.CONTAINERS_SIZE))
        except Exception:
            print(print_exc())
        finally:
            return flags, messages, results
        
    def get_token_owner(self, host, token):
        return self.genericGet(host, token, "user")

    def handle_check(self, messages, flagged_asset, asset_type, flag_condition):
        if flagged_asset == True:
            messages.add_flag_message(asset_type, flag_condition)
        return flagged_asset
    
    def get_user_data(self, u):
        return from_dict(data_class=User, data=u)
