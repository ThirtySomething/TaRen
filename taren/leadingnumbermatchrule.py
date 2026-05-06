import re

from taren.episodematchrule import EpisodeMatchRule


class LeadingNumberMatchRule(EpisodeMatchRule):
    def try_match(self, filename: str, episode: "Episode") -> bool | None:
        filename_match = re.search(r"(^[0-9]{4} )", filename)
        if not filename_match:
            return None
        filename_id: int = int(filename_match.group(1))
        return episode.episode_id == filename_id
