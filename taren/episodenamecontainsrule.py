from taren.episodematchrule import EpisodeMatchRule


class EpisodeNameContainsRule(EpisodeMatchRule):
    def try_match(self, filename: str, episode: "Episode") -> bool | None:
        return episode.episode_name.lower() in filename.lower()
