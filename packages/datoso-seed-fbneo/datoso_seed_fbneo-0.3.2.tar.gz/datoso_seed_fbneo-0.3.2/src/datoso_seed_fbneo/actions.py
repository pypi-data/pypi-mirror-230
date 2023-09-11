from datoso_seed_fbneo.dats import FbneoDat

actions = {
    '{dat_origin}/full': [
        {
            'action': 'LoadDatFile',
            '_class': FbneoDat
        },
        {
            'action': 'DeleteOld'
        },
        {
            'action': 'Copy',
            'folder': '{dat_destination}'
        },
        {
            'action': 'SaveToDatabase'
        }
    ],
    '{dat_origin}/light': [
        {
            'action': 'LoadDatFile',
            '_class': FbneoDat
        },
        {
            'action': 'DeleteOld'
        },
        {
            'action': 'Copy',
            'folder': '{dat_destination}'
        },
        {
            'action': 'SaveToDatabase'
        }
    ]
}

def get_actions():
    return actions