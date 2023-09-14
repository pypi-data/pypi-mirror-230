import ipaddress
from typing import Tuple
from ipaddress import ip_network


def _formalize(cidrs: list[str]):
    def to_network(n):
        return ip_network(n)

    cidrs = map(to_network, cidrs)
    return list(ipaddress.collapse_addresses(cidrs))


def _has_overlap(network, list_of_networks):
    for n in list_of_networks:
        if network.overlaps(n):
            return True


def _is_subnet(network, list_of_networks):
    for n in list_of_networks:
        if network.subnet_of(n):
            return True


def find_available_cidr_24(total_cidrs: list[str], used_cidrs: list[str], configured_cidrs: list[str]):
    total_cidrs = _formalize(total_cidrs)
    used_cidrs = _formalize(used_cidrs)
    configured_cidrs = _formalize(configured_cidrs)

    for t in configured_cidrs:
        for space in t.subnets(new_prefix=24):
            if not _is_subnet(space, total_cidrs):
                continue
            if _has_overlap(space, used_cidrs):
                continue
            return str(space)


def subnets_of(input: list[str], limit: list[str]) -> Tuple[bool, str]:
    input = _formalize(input)
    limit = _formalize(limit)
    for i in input:
        if not _is_subnet(i, limit):
            return False, str(i)
    return True, None


def overlaps(a: list[str], b: list[str]) -> Tuple[bool, str]:
    a = _formalize(a)
    b = _formalize(b)

    for i in a:
        if _has_overlap(i, b):
            return True, i
    return False, None
