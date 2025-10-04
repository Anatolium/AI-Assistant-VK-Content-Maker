import requests
import datetime


class VKStats:
    def __init__(self, vk_api_key, group_id):
        self.vk_api_key = vk_api_key
        self.group_id = group_id

    def get_stats(self, start_date, end_date):
        url = 'https://api.vk.com/method/stats.get'
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        start_date = start_date.replace(tzinfo=datetime.timezone.utc)
        end_date = end_date.replace(tzinfo=datetime.timezone.utc)

        start_unix_time = int(start_date.timestamp())
        end_unix_time = int(end_date.timestamp())

        params = {
            'access_token': self.vk_api_key,
            'v': '5.199',
            'group_id': self.group_id,
            'timestamp_from': start_unix_time,
            'timestamp_to': end_unix_time
        }
        response = requests.get(url, params=params).json()

        # для отладки можно включить
        # import json
        # print(json.dumps(response, indent=2, ensure_ascii=False))

        if 'error' in response:
            raise Exception(response['error']['error_msg'])
        else:
            return response['response']  # возвращаем список, а не только [0]

    def get_followers(self):
        url = 'https://api.vk.com/method/groups.getMembers'
        params = {
            'access_token': self.vk_api_key,
            'v': '5.199',
            'group_id': self.group_id
        }
        response = requests.get(url, params=params).json()
        if 'error' in response:
            raise Exception(response['error']['error_msg'])
        else:
            return response['response']['count']


    def display_stats(self, stats):
        print(f"{'Дата':<12}{'Просмотры':<10}{'Посетители':<11}{'Охват':<10}{'Охват подписчиков':<12}")

        total_views = 0
        total_visitors = 0
        total_reach = 0
        total_reach_subs = 0

        for day_stats in stats:
            date = datetime.datetime.fromtimestamp(day_stats['period_from']).strftime("%Y-%m-%d")

            views = day_stats['visitors'].get('views', 0)
            visitors = day_stats['visitors'].get('visitors', 0)
            reach = day_stats['reach'].get('reach', 0)
            reach_subs = day_stats['reach'].get('reach_subscribers', 0)

            total_views += views
            total_visitors += visitors
            total_reach += reach
            total_reach_subs += reach_subs

            print(f"{date:<12}{views:<10}{visitors:<11}{reach:<10}{reach_subs:<12}")

        print("-" * 60)
        print(f"{'TOTAL':<12}{total_views:<10}{total_visitors:<11}{total_reach:<10}{total_reach_subs:<12}")


# Пример использования:
if __name__ == "__main__":
    from config import VK_API_KEY, VK_GROUP_ID

    vk_api_key = VK_API_KEY
    group_id = VK_GROUP_ID
    start_date = '2025-10-01'
    end_date = '2025-10-05'

    vk_stats = VKStats(vk_api_key, group_id)
    stats = vk_stats.get_stats(start_date, end_date)
    vk_stats.display_stats(stats)
