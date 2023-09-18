class K8M():
  def __init__(self) -> None:
    super().__init__()
    self.ksapi_ip: str = None
    self.username: str = None
    self.password: str = None
    self.token: str = None
    self.new_kubeconfig: str = None
    self.old_kubeconfig: str = None

var = K8M()