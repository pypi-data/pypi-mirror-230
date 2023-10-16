class SystemUsageError(Exception):
    """
    When CPU, Memory or Disk usage is over 90%, raise this error
    """
    pass
