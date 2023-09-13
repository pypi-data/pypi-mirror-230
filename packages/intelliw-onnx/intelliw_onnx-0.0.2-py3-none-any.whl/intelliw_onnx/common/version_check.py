from packaging.version import Version, parse


def check(sw, version, target=''):
    sw_target = Version(target)
    sw_version = parse(version)
    if sw_version != sw_target:
        print('####################################################')
        print('WARNING: your', sw, 'version is', version)
        print('suggested version is', target)
        print('####################################################')
