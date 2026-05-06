import re

from taren.episodematchrule import EpisodeMatchRule


class DailymotionTokenMatchRule(EpisodeMatchRule):
    def try_match(self, filename: str, episode: "Episode") -> bool | None:
        filename_match = re.search(r"(_E([0-9]{3,4})_)", filename)
        if not filename_match:
            return None
        filename_id: int = int(filename_match.group(2))
        return episode.episode_id == filename_id
