""" Kameleoon SDK version """

from typing import Optional, Tuple


version_info = (2, 4, 0)
__version__ = ".".join(str(v) for v in version_info)  # uses in scripts


class SdkVersion:
    """SdkVersion is a helper class for get name and version of sdk"""

    NAME = "PYTHON"
    VERSION = __version__

    @staticmethod
    def get_version_components(version_string: str) -> Optional[Tuple[int, int, int]]:
        """Get integer components from string version"""
        versions = [0, 0, 0]
        version_parts = version_string.split(".")

        for i in range(min(len(versions), len(version_parts))):
            try:
                versions[i] = int(version_parts[i])
            except ValueError:
                print(f"Invalid version component, index: {i}, value: {version_parts[i]}")
                return None

        return (versions[0], versions[1], versions[2])

    @staticmethod
    def get_float_version(version_string: str) -> Optional[float]:
        """Get float version from string (only major and minor are considered)"""
        version_components = SdkVersion.get_version_components(version_string)
        if version_components is None:
            return None

        major, minor, _ = version_components
        return float(f"{major}.{minor}")
