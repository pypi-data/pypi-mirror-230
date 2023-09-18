from __future__ import annotations


class OrganizationConfigOutput(dict):
    @property
    def df_statistics_row_threshold(self) -> int:
        return int(self["dfStatisticsRowThreshold"])


class OrgConfigOutput(dict):
    @property
    def configuration(self) -> OrganizationConfigOutput:
        return OrganizationConfigOutput(self["organization"]["configuration"])
