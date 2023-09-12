from sys import exit as sys_exit
import xlsxwriter
from dacite import from_dict
from gitlab_ps_utils.json_utils import json_pretty
from gitlab_ps_utils.api import GitLabApi
from gitlab_ps_utils.processes import MultiProcessing
from gitlab_ps_utils.misc_utils import is_error_message_present
from gitlab_evaluate.lib import utils, api as evaluateApi
from gitlab_evaluate.lib.api_models.application_stats import GitLabApplicationStats


class ReportGenerator():
    def __init__(self, host, token, filename=None, output_to_screen=False, evaluate_api=None, processes=None):
        self.host = host
        self.token = token
        self.evaluate_api = evaluate_api if evaluate_api else evaluateApi.EvaluateApi(GitLabApi())
        self.validate_token()
        if filename:
            self.workbook = xlsxwriter.Workbook(f'{filename}.xlsx')
        else:
            self.workbook = xlsxwriter.Workbook('evaluate_report.xlsx')
        self.app_stats = self.workbook.add_worksheet('App Stats')
        self.final_report = self.workbook.add_worksheet('Evaluate Report')
        self.workbook.add_format({'text_wrap': True})
        self.flagged_projects = self.workbook.add_worksheet('Flagged Projects')
        self.using_admin_token = self.is_admin_token()
        self.users = self.workbook.add_worksheet('Users')
        self.raw_output = self.workbook.add_worksheet('Raw Project Data')
        self.output_to_screen = output_to_screen
        self.multi = MultiProcessing()
        self.processes = processes
        self.csv_columns = [
            'Project',
            'ID',
            'URL',
            'kind',
            'namespace',
            'archived',
            'last_activity_at',
            'Pipelines',
            'Pipelines_over',
            'Issues',
            'Issues_over',
            'Branches',
            'Branches_over',
            'commit_count',
            'commit_count_over',
            'Merge Requests',
            'Merge Requests_over',
            'storage_size',
            'storage_size_over',
            'repository_size',
            'repository_size_over',
            'wiki_size',
            "lfs_objects_size",
            "lfs_objects_size_over",
            "job_artifacts_size",
            "job_artifacts_size_over",
            "snippets_size",
            "snippets_size_over",
            "uploads_size",
            "uploads_size_over",
            'Tags',
            'Tags_over',
            'Package Types In Use',
            'Total Packages Size',
            'Container Registry Size',
            'Estimated Export Size']
        self.report_headers = [
            'Project',
            'Reason'
        ]
        self.user_headers = [
            'username',
            'email',
            'state',
            'using_license_seat'
        ]
        utils.write_headers(self.raw_output, self.csv_columns)
        utils.write_headers(self.flagged_projects, self.csv_columns)
        utils.write_headers(self.final_report, self.report_headers)
        utils.write_headers(self.users, self.user_headers)
        self.final_report.set_default_row(150)
        self.final_report.set_row(0, 20)

    def write_workbook(self):
        self.app_stats.autofit()
        self.final_report.autofit()
        self.flagged_projects.autofit()
        self.raw_output.autofit()
        self.users.autofit()
        self.workbook.close()

    def handle_getting_data(self, group_id):
        # Determine whether to list all instance or all group projects (including sub-groups)
        endpoint = f"/groups/{group_id}/projects?include_subgroups=true&with_shared=false" if group_id else "/projects?statistics=true"
        for flags, messages, results in self.multi.start_multi_process_stream_with_args(self.evaluate_api.get_all_project_data, self.evaluate_api.gitlab_api.list_all(
            self.host, self.token, endpoint), self.host, self.token, processes=self.processes):
            self.write_output_to_files(flags, messages, results)
    
    def handle_getting_user_data(self, group_id=None):
        endpoint = f"groups/{group_id}/members" if group_id else "/users"
        for user in self.multi.start_multi_process_stream(self.evaluate_api.get_user_data, self.evaluate_api.gitlab_api.list_all(
            self.host, self.token, endpoint), processes=self.processes):
                utils.append_to_workbook(self.users, [user.to_dict()], self.user_headers)

    def get_app_stats(self, source, token):
        report_stats = []
        error, resp = is_error_message_present(self.evaluate_api.getApplicationInfo(source, token))
        if not error:
            app_stats = from_dict(data_class=GitLabApplicationStats, data=resp)
            report_stats += [
                ('Basic information from source', source),
                ('Total Users', app_stats.users),
                ('Total Active Users', app_stats.active_users),
                ('Total Groups', app_stats.groups),
                ('Total Projects', app_stats.projects),
                ('Total Merge Requests', app_stats.merge_requests),
                ('Total Forks', app_stats.forks),
                ('Total Issues', app_stats.issues),
                ('Total Archived Projects', self.evaluate_api.getArchivedProjectCount(source,token))
            ]
        else:
            print(f"Warning: Unable to pull application info from URL: {source}")

        if resp := self.evaluate_api.getVersion(source, token):
            if len(report_stats) > 0:
                report_stats.insert(1, ('GitLab Version', resp.get('version')))
            else:
                report_stats.append(('GitLab Version', resp.get('version')))
        else:
            print(f"Unable to pull application info from URL: {source}")
        
        for row, stat in enumerate(report_stats):
            self.app_stats.write(row, 0, stat[0])
            self.app_stats.write(row, 1, stat[1])

    def write_output_to_files(self, flags, messages, results):
        dict_data = []
        dict_data.append({x: results.get(x) for x in self.csv_columns})
        utils.append_to_workbook(self.raw_output, dict_data, self.csv_columns)

        if True in flags:
            utils.append_to_workbook(self.flagged_projects, dict_data, self.csv_columns)
            utils.append_to_workbook(self.final_report, [{'Project': results.get('Project'), 'Reason': messages.generate_report_entry()}], self.report_headers)
        if self.output_to_screen:
            print(f"""
            {'+' * 40}
            {json_pretty(results)}
            """)
    
    def validate_token(self):
        error, resp = is_error_message_present(self.evaluate_api.get_token_owner(self.host, self.token))
        if error:
            print("\nToken appears to be invalid. See API response below. Exiting script")
            print(resp)
            sys_exit(1)

    def is_admin_token(self):
        user = self.evaluate_api.get_user_data(self.evaluate_api.get_token_owner(self.host, self.token))
        return user.is_admin
