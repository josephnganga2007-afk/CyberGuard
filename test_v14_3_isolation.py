import os,tempfile,database
def run():
    old=database.DATABASE; fd,path=tempfile.mkstemp(suffix=".db"); os.close(fd)
    try:
        database.DATABASE=path; database.initialize_database()
        b1=database.create_business("B1","b1@test"); b2=database.create_business("B2","b2@test")
        s1=database.add_supplier("ABC Supplies","a@test","4821"); s2=database.add_supplier("ABC Supplies","a@test","7319")
        database.link_supplier_to_business(b1,s1); database.link_supplier_to_business(b2,s2)
        database.save_transaction("ABC Supplies","B1 tx",90,"CRITICAL",business_id=b1)
        database.save_transaction("ABC Supplies","B2 tx",15,"LOW",business_id=b2)
        assert [x["message"] for x in database.get_supplier_history("ABC Supplies",b1)]==["B1 tx"]
        assert [x["message"] for x in database.get_supplier_history("ABC Supplies",b2)]==["B2 tx"]
        database.save_transaction("ABC Supplies","gmail",80,"CRITICAL",gmail_message_id="same",business_id=b1)
        assert database.gmail_message_exists("same",b1)
        assert not database.gmail_message_exists("same",b2)
        i=database.save_investigation("ABC Supplies","a@test","x","B1 inv",None,50,"MEDIUM",business_id=b1,gmail_message_id="inv")
        database.save_investigation("ABC Supplies","a@test","x","B2 inv",None,50,"MEDIUM",business_id=b2,gmail_message_id="inv")
        assert database.review_investigation(i,"SUSPICIOUS",business_id=b2) is False
        assert database.review_investigation(i,"SUSPICIOUS",business_id=b1) is True
        print("V14.3 BUSINESS ISOLATION TEST: PASS")
    finally:
        database.DATABASE=old
        try:os.remove(path)
        except OSError:pass
if __name__=="__main__":run()
