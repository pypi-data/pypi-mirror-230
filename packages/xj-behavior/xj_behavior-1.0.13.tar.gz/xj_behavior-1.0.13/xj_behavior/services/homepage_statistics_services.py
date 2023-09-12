import datetime
from orator import DatabaseManager
from decimal import Decimal
from ..utils.j_config import JConfig
from ..utils.j_dict import JDict
from main.settings import BASE_DIR
from pathlib import Path
from xj_behavior.utils.execl import ExcelGenerator
from config.config import JConfig as JConfigs

module_root = str(Path(__file__).resolve().parent)
# 配置之对象
main_config_dict = JDict(JConfig.get_section(path=str(BASE_DIR) + "/config.ini", section="xj_behavior"))
module_config_dict = JDict(JConfig.get_section(path=str(BASE_DIR) + "/config.ini", section="xj_behavior"))

download_path = main_config_dict.download_path or module_config_dict.download_path or ""

config = JConfigs()
db_config = {
    config.get('main', 'driver', "mysql"): {
        'driver': config.get('main', 'driver', "mysql"),
        'host': config.get('main', 'mysql_host', "127.0.0.1"),
        'database': config.get('main', 'mysql_database', ""),
        'user': config.get('main', 'mysql_user', "root"),
        'password': config.get('main', 'mysql_password', "123456"),
        "port": config.getint('main', 'mysql_port', "3306")
    }
}
db = DatabaseManager(db_config)


class HomepageStatisticsServices():
    @staticmethod
    def statistics(params: dict = None):
        deal_orders = db.table('enroll_enroll').where_in('enroll_status_code', [80, 668]).count()
        number_escorters = db.table(db.raw(f"role_user_to_role as r1")).left_join(db.raw(f"role_role as r2"),
                                                                                  'r1.role_id',
                                                                                  '=', 'r2.id').where_in('role',
                                                                                                         ['BX-WORKER',
                                                                                                          'CASUAL_WORKER']).count()
        bid_winning_amount = db.table('thread').sum('field_2')

        statistics = {
            'deal_orders': deal_orders,
            'number_escorters': number_escorters,
            'bid_winning_amount': bid_winning_amount if bid_winning_amount else Decimal('0.0')
        }
        return statistics, None


class InviteeServices():
    @staticmethod
    def invitee_export(request_params):
        create_time_start = request_params.get('create_time_start', "")
        create_time_end = request_params.get('create_time_end', "")
        query = db.table('user_relate_to_user as r') \
            .select(
            "parent.user_name as inviter_nickname",
            "detail_parent.real_name as inviter_real_name",
            "child.user_name as invitee_nickname",
            "detail_child.real_name as invitee_real_name",
            db.raw(f"DATE_FORMAT(r.created_time, '%%Y-%%m-%%d %%H:%%i:%%s') as invitation_time")
        ) \
            .left_join("user_base_info as child", 'r.user_id', '=', 'child.id') \
            .left_join("user_base_info as parent", 'r.with_user_id', '=', 'parent.id') \
            .left_join("user_detail_info as detail_child", 'r.user_id', '=', 'detail_child.user_id') \
            .left_join("user_detail_info as detail_parent", 'r.with_user_id', '=', 'detail_parent.user_id') \
            .where('r.user_relate_type_id', '=', 1) \
            .where('r.user_id', '!=', 'r.with_user_id') \
            .where('child.is_delete', '=', 0) \
            .where('parent.is_delete', '=', 0)
        if create_time_start and create_time_end:
            query.where_raw(
                "r.created_time >= '" + create_time_start + "'and r.created_time <= '" + create_time_end + "'")
        data = query.get().items

        header = {
            "inviter_nickname": "邀请人昵称",
            "inviter_real_name": "邀请人真实姓名",
            "invitee_nickname": "被邀请人昵称",
            "invitee_real_name": "被邀请人真实姓名",
            "invitation_time": "邀请时间",
        }
        excel_generator = ExcelGenerator(data, header)
        now = datetime.datetime.now()  # 获取当前日期和时间
        timestamp = now.strftime("%Y%m%d%H%M%S")  # 格式化日期和时间
        filepath = download_path + now.strftime("%Y-%m") + f"/邀请文件_{timestamp}.xlsx"  # 在文件名中添加时间戳
        path = excel_generator.generate_excel_response(filepath)
        return path, None
