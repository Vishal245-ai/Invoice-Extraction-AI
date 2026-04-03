def is_duplicate(new, existing_list):
    for inv in existing_list:
        if (
            inv["invoice_number"] == new["invoice_number"]
            and inv["vendor_name"] == new["vendor_name"]
            and inv["total"] == new["total"]
        ):
            return True
    return False