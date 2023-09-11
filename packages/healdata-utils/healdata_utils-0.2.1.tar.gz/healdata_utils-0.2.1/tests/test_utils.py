from healdata_utils.utils import sync_fields


def test_add_missing_fields():
    # data (note one var not in schema)
    data = [
        {"var2": 2, "var3": 3, "var1": 1},
        {
            "var5": 10,
            "var4": 9,
            "var1": 1,
        },
    ]
    # fields from schema
    fields = ["var1", "var2", "var3", "var4"]

    data_with_missing = sync_fields(data, fields)
    assert data_with_missing == [
        {"var1": 1, "var2": 2, "var3": 3, "var4": None},
        {"var1": 1, "var2": None, "var3": None, "var4": 9, "var5": 10}
    ]