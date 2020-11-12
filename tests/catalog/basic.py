from openpecha.catalog.storage import GithubBucket

if __name__ == "__main__":
    bucket = GithubBucket("OpenPecha")
    for pecha_id, base in bucket.get_all_pechas_base():
        print(pecha_id)
        for vol_base in base:
            print(vol_base)
