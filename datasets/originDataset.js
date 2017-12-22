export const data = {
    originDataset: {
        'uid': 'String',
        'time': 'timestamp',
        'lat': 'double',
        'lng': 'double',
        'state': 'S/T/U',
        'stateID': 'number',
        'admin': 'text',
        'example': ['1', 12312321312, 39, 110, T, 1, '海淀区']
    },
    outputRawData: {
        id: 'String',
        seg: 'Number',
        hour: 'Number', // 0-23
        wday: 'Number', // 0-6
        gid: 'Number',
        state: 'S/T',
        admin: 'Number', // 1-16
        from_gid: 'Number',
        to_gid: 'Number',
        from_aid: 'Number',
        to_aid: 'Number'
    }
}