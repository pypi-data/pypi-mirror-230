import responses
from ..models import Group


class Groups:
    """
    Operations for working with groups.

    Methods correspond to end points laid out at:

    https://learn.microsoft.com/en-us/rest/api/power-bi/groups

    Parameters
    ----------
    `client` : `PowerBI`
        pbipy PowerBI client for handling interactions with API.
    """

    def __init__(self, client):
        self.client = client
    
    def get_groups(self, filter=None, top=None, skip=None):
        """
        Return a list of workspaces the user has access to.

        Parameters
        ----------
        `filter` : `str`
            Filters the results, based on a boolean condition, by default None
        `top` : `int`
            Returns only the first n results, by default None
        `skip` : `int`
            Skip the first n results, by default None

        Returns
        -------
        `list`
            List of `Group` objects.
        """

        resource = "https://api.powerbi.com/v1.0/myorg/groups"
        params = {
            "$filter": filter,
            "$top": top,
            "$skip": skip,
        }
        return self.client._get_and_load_resource(resource, model=Group, parameters=params)


@responses.activate
def test_get_dataset_group_property_is_set(powerbi, get_dataset):
    responses.get(
        "https://api.powerbi.com/v1.0/myorg/groups/f089354e-8366-4e18-aea3-4cb4a3a50b48/datasets/cfafbeb1-8037-4d0c-896e-a46fb27ff229",
        body=get_dataset,
        content_type="application/json",
    )

    dataset = powerbi.dataset(
        "cfafbeb1-8037-4d0c-896e-a46fb27ff229",
        group="f089354e-8366-4e18-aea3-4cb4a3a50b48",
    )

    assert dataset.group_id == "f089354e-8366-4e18-aea3-4cb4a3a50b48"

