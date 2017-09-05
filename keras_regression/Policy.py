import pandas


def remove_invalid_entries(df):
    invalid_list = df.index[df['Verpackungseinheit'] == 'unknown'].tolist()
    df = df.drop(invalid_list)
    invalid_list = []
    for index, row in df.iterrows():
        this_price = float(row['price'])
        this_color = row['Farbe']
        this_package_size = float(row['Verpackungseinheit'])
        if is_white(this_color):
            if float(this_price) / this_package_size > 0.2:
                invalid_list.append(index)
    return df.drop(invalid_list)


def is_white(color):
    if color == 'weiss':
        return True
    else:
        return False
