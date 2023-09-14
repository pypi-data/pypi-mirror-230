def set_api_detail(cls, key, data):
    if not hasattr(cls, 'api_detail'):
        setattr(cls, 'api_detail', {key: data})
    else:
        api_detail = getattr(cls, 'api_detail')
        api_detail[key] = data
        setattr(cls, 'api_detail', api_detail)


def add_element_to_api_detail(cls, key, data):
    if not hasattr(cls, 'api_detail'):
        setattr(cls, 'api_detail', {key: [data]})
    else:
        api_detail = getattr(cls, 'api_detail')
        if key not in api_detail:
            api_detail[key] = [data]
        else:
            append_data = api_detail[key]
            append_data.append(data)
            api_detail[key] = append_data
        setattr(cls, 'api_detail', api_detail)


def get_dependencies_next_index(cls) -> int:
    if not hasattr(cls, 'api_detail'):
        return 0
    else:
        api_detail = getattr(cls, 'api_detail')
        if 'dependencies' not in api_detail:
            return 0
        else:
            return len(api_detail['dependencies'])
