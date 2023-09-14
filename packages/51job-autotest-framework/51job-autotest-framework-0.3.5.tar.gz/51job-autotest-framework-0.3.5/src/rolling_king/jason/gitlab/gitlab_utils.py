#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import logging

from rolling_king.autotest.requests.http_sender_module import HttpSender

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
logger = logging.getLogger("gitlab_utils")


class GitLab(object):
    __ACCESS_SEG_1: str = "glpat"
    __ACCESS_SEG_2: str = "Y4AGLX1aWBkvvsyjqEuv"
    __access_token: str = None
    __host_url: str = None
    __http_sender: HttpSender = None

    @classmethod
    def init(cls, gitlab_host_url: str, personal_access_token: str = None):
        if personal_access_token is None:
            cls.__access_token = cls.__ACCESS_SEG_1 + "-" + cls.__ACCESS_SEG_2
        else:
            cls.__access_token = personal_access_token
        if gitlab_host_url is not None and len(gitlab_host_url) > 0:
            cls.__host_url = gitlab_host_url
            cls.__http_sender = HttpSender(hostname=cls.__host_url,
                                           headers={"PRIVATE-TOKEN": cls.__access_token})
        else:
            logger.error("Please provide gitlab_host_url")

    @classmethod
    def get_token(cls):
        logger.info(f"Personal Access Token = {cls.__access_token}")

    @classmethod
    def get_host_url(cls):
        logger.info(f"GitLab Host URL = {cls.__host_url}")

    @classmethod
    def get_all_projects(cls) -> dict:
        cls.__http_sender.send_get_request_by_suburi(sub_uri="/api/v4/projects",
                                                     input_params={
                                                         "private_token": cls.__access_token
                                                     })
        # try:
        json_resp = cls.__http_sender.get_response.json()
        if len(json_resp) > 0:
            logger.info(f"Total {len(json_resp)} projects")
            for curr in json_resp:
                logger.info(f"id = {curr['id']}, name = {curr['name']}, default_branch = {curr['default_branch']}")
            return json_resp
        else:
            return {}
        # except e:
        #     logger.error("Exception happened...{e.args}")

    @classmethod
    def get_specific_project(cls, project_name: str) -> dict | None:
        # "private_token": cls.__access_token, # 若header中没有PRIVATE-TOKEN则需要参数里写上。
        cls.__http_sender.send_get_request_by_suburi("/api/v4/projects",
                                                     input_params={
                                                         "search": project_name
                                                     })
        # cls.__http_sender.send_get_request(full_get_url="https://gitdev.51job.com/api/v4/projects?search=maven-jave-project")
        json_resp = cls.__http_sender.get_response.json()
        if json_resp is not None and len(json_resp) == 1:
            logger.info(f"[成功]: 响应为{json_resp}")
            return json_resp[0]
        else:
            return {}

    @classmethod
    def get_project_branches(cls, project_id: str = None, project_name: str = None) -> list[dict] | None:
        if project_id is None or project_id == "":
            project_id = cls.get_specific_project(project_name)['id']
        cls.__http_sender.send_get_request_by_suburi(
            # "private_token": cls.__access_token, # 若header中没有PRIVATE-TOKEN则需要参数里写上。
            sub_uri=f"/api/v4/projects/{project_id}/repository/branches",
            input_params={
                # "private_token": cls.__access_token
            }
        )
        json_resp = cls.__http_sender.get_response.json()
        logger.info(json_resp)
        return json_resp

    @classmethod
    def get_all_merge_requests_by_project(cls, project_id: str) -> list[dict]:
        cls.__http_sender.send_get_request_by_suburi(
            sub_uri=f"/api/v4/projects/{project_id}/merge_requests?state=all",
            input_params={}
        )
        return cls.__http_sender.get_response.json()  # 默认按created_at排序，最近的是第一个。

    @classmethod
    def add_comments_for_merge_request(cls, note: str, project_id: str, merge_request_id: str):
        cls.__http_sender.send_json_post_request_by_suburi(
            # "private_token": cls.__access_token, # 若header中没有PRIVATE-TOKEN则需要参数里写上。
            sub_uri=f"/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/notes",
            json_data={
                "body": note
            }
        )
        logger.info(cls.__http_sender.post_response.text)


if __name__ == '__main__':
    GitLab.init(gitlab_host_url="https://gitdev.51job.com")
    GitLab.get_token()
    GitLab.get_host_url()
    # GitLab.get_all_projects()
    # GitLab.get_specific_project(project_name="maven-jave-project")
    # GitLab.get_project_branches(project_name="maven-jave-project")
    # Add Comment for latest MR of a particular project by its name #
    pro_id = GitLab.get_specific_project(project_name="maven-jave-project")['id']
    dict_list = GitLab.get_all_merge_requests_by_project(project_id=pro_id)
    mr_id = dict_list[0]['iid']
    GitLab.add_comments_for_merge_request("Script Added", pro_id, mr_id)
