#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   tag.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Tag API
'''

from datature.http.resource import RESTResource


class Tag(RESTResource):
    """Datature Tag API Resource."""

    @classmethod
    def list(cls) -> dict:
        """Lists all tags in the project.

        :return: A list of dictionaries containing tag metadata with the following structure:

                .. code-block:: json

                        [
                            {
                                "index": 0,
                                "name": "tagName1"
                            }
                        ]

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Tag.list()
        """
        return cls.request("GET", "/tag/list")

    @classmethod
    def create(cls, name: str) -> dict:
        """Creates a new tag. The indices of new tags created will begin from the last existing tag index.

        :param name: The name of the new tag.
        :return: An updated list of dictionaries containing tag metadata with the following structure:

                .. code-block:: json

                        [
                            {
                                "index": 0,
                                "name": "tagName1"
                            }, {
                                "index": 1,
                                "name": "tagName2"
                            }
                        ]

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Tag.create("tagName2")
        """
        return cls.request("POST", "/tag", request_body={"name": name})

    @classmethod
    def modify(cls, index: int, name: str) -> dict:
        """Updates the name of a specific tag using the tag index.

        :param index: The index of the tag to update.
        :param name: The new name of the tag.
        :return: An updated list of dictionaries containing tag metadata with the following structure:

                .. code-block:: json

                        [
                            {
                                "index": 0,
                                "name": "tagName1"
                            }, {
                                "index": 1,
                                "name": "tagName3"
                            }
                        ]

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Tag.modify(1, "tagName3")
        """
        return cls.request("PUT", f"/tag/{index}", request_body={"name": name})

    @classmethod
    def delete(cls, index: int) -> dict:
        """Deletes a specific tag using the tag index. The tag indices of other tags will be left unchanged. The indices of new tags created will begin from the last existing tag index.

        :param index: The index of the tag.
        :return: A dictionary containing the deletion status of the tag with the following structure:

                .. code-block:: json

                        {
                            "deleted": true
                        }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Tag.delete(1)
        """
        return cls.request("DELETE", f"/tag/{index}")
