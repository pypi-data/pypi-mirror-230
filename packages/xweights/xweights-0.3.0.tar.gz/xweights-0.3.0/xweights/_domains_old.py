import cordex as cx


class Domains:
    """The :class:`Domains` opens all domains provided by py-cordex
    https://py-cordex.readthedocs.io/en/stable/domains.html

    **Attributes:**
        *domains:*
            Information of CORDEX domains
    """

    def __init__(self):
        self.domains = cx.domain.domain_names()


domains = Domains()


def which_domains():
    """List of all available CORDEX domains

    Returns
    -------
    List - list
        List of CORDEX domains

    """
    return domains.domains


def get_domain(domain):
    """Creates an xarray dataset containg the domain grid definitions.
    Grid boundaries in the global coordinates are added
    (lon_verticces, lat_vertices).

    Parameters
    ----------
    domain: str
        Name of the CORDEX domain

    Returns
    -------
    Dataset : xr.Dataset
        Dataset containing the coordinates

    Example
    -------
    To create a CORDEX EUR-11 rotated pole domain dataset::

        import xweights as xw

        eur11 = xw.get_domain('EUR-11')
    """
    return cx.cordex_domain(domain, add_vertices=True)
