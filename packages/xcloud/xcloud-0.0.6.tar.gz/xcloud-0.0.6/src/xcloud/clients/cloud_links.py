from xcloud.utils.requests_utils import do_request
from xcloud.config import Config
from xcloud.dtypes.cloud_links import Link
from typing import List, Optional


class LinksClient:
    
    @classmethod
    def get_links(cls, workspace_id: Optional[str] = None) -> List[Link]:        
        response = do_request(
            url="{}/v1/links/".format(
                Config.CLOUD_LINKS_BASE_URL_X_BACKEND
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        list_link_dicts = response.json()["data"]
        links = []
        
        for link_dict in list_link_dicts:
            link = Link.parse_obj(link_dict)
            links.append(link)
            
        return links
    
    @classmethod
    def get_link_by_name(cls, link_name: str, workspace_id: Optional[str] = None) -> Link:        
        response = do_request(
            url="{}/v1/links/{}".format(
                Config.CLOUD_LINKS_BASE_URL_X_BACKEND,
                link_name
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        link_dict = response.json()["data"]
        link = Link.parse_obj(link_dict)
        
        return link
    
    @classmethod
    def delete_link(cls, link_name: str, reason: str = "", workspace_id: Optional[str] = None) -> Link:
        response = do_request(
            url="{}/v1/links/{}".format(
                Config.CLOUD_LINKS_BASE_URL_X_BACKEND,
                link_name
            ),
            params={
                "reason": reason
            },
            http_method="delete",
            workspace_id=workspace_id
        )
        
        link_dict = response.json()["data"]
        link = Link.parse_obj(link_dict)
        return link
    
    @classmethod
    def create_link(cls, link: Link, reason: str = "", workspace_id: Optional[str] = None) -> Link:        
        link_dict = link.dict()
        
        response = do_request(
            url="{}/v1/links/".format(
                Config.CLOUD_LINKS_BASE_URL_X_BACKEND
            ),
            params={
                "reason": reason
            },
            http_method="post",
            json_data=link_dict,
            workspace_id=workspace_id
        )
        
        returned_link_dict = response.json()["data"]
        returned_link = Link.parse_obj(returned_link_dict)
        
        return returned_link
