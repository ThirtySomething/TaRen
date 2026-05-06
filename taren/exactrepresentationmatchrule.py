from taren.episodematchrule import EpisodeMatchRule


class ExactRepresentationMatchRule(EpisodeMatchRule):
    def try_match(self, filename: str, episode: "Episode") -> bool | None:
        if str(episode) == filename:
            return True
        return None
