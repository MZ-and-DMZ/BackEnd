from datetime import datetime, timedelta


async def is_unused(client, user_name):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=20)
    response = client.lookup_events(
        LookupAttributes=[
            {
                "AttributeKey": "Username",
                "AttributeValue": user_name,
            },
        ],
        StartTime=start_date,
        EndTime=end_date,
        MaxResults=1,  # 결과의 최대 개수 (조정 가능)
    )
    if not response["Events"]:
        return user_name
