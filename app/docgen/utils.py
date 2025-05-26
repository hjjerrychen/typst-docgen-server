import git

class Version:
  
  @classmethod
  def get_git_hash_version(cls, short: bool = True) -> str:
      repo = git.Repo(search_parent_directories=True)
      sha = repo.head.commit.hexsha
      return repo.git.rev_parse(sha, short=4) if short else sha