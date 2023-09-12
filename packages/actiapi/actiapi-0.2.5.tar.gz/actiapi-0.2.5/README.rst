*******
ActiAPI
*******
This library is **only** meant to serve as an example of how to use ActiGraph's API to
retrieve data from ActiGraph devices.

Please refer to official API documentation
(https://github.com/actigraph/StudyAdminAPIDocumentation and
https://github.com/actigraph/CentrePoint3APIDocumentation).

Please do not contact ActiGraph support for questions related to this library. You can
create issues on this repository and we'll do our best to help you.

Example
=======

Metadata
--------

>>> from actiapi.v3 import ActiGraphClientV3
    api_client = ActiGraphClientV3(<api_access_key>, <api_secret_key>)
    metadata = api_client.get_study_metadata(<study_id>)
    metadata = {x["id"]: x for x in metadata}

Raw data
--------

>>> from actiapi.v3 import ActiGraphClientV3
    api_client = ActiGraphClientV3(<api_access_key>, <api_secret_key>)
    results: List[str] = api_client.get_files(
        user=<user_id>, study_id=<self.study_id>
    )

