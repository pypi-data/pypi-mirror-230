import numpy as np
from tc_core_analyzer_lib.assess_engagement import EngagementAssessment
from tc_core_analyzer_lib.utils.activity import DiscordActivity


def test_disengaged_members():
    acc_names = []
    acc_count = 10
    for i in range(acc_count):
        acc_names.append(f"user{i}")

    acc_names = np.array(acc_names)

    # four weeks
    max_interval = 50

    # preparing empty joined members dict
    all_joined = dict(
        zip(np.array(range(max_interval), dtype=str), np.repeat(set(), max_interval))
    )

    activity_dict = {
        "all_joined": {},
        "all_joined_day": all_joined,
        "all_consistent": {},
        "all_vital": {},
        "all_active": {},
        "all_connected": {},
        "all_paused": {},
        "all_new_disengaged": {},
        "all_disengaged": {},
        "all_unpaused": {},
        "all_returned": {},
        "all_new_active": {},
        "all_still_active": {},
        "all_dropped": {},
        "all_disengaged_were_newly_active": {},
        "all_disengaged_were_consistently_active": {},
        "all_disengaged_were_vital": {},
        "all_lurker": {},
        "all_about_to_disengage": {},
        "all_disengaged_in_past": {},
    }
    memberactivities = activity_dict.keys()

    INT_THR = 1  # minimum number of interactions to be active
    UW_DEG_THR = 1  # minimum number of accounts interacted with to be active
    PAUSED_T_THR = 1  # time period to remain paused
    CON_T_THR = 4  # time period to be consistent active
    CON_O_THR = 3  # time period to be consistent active
    EDGE_STR_THR = 5  # minimum number of interactions for connected
    UW_THR_DEG_THR = 5  # minimum number of accounts for connected
    VITAL_T_THR = 4  # time period to assess for vital
    VITAL_O_THR = 3  # times to be connected within VITAL_T_THR to be vital
    STILL_T_THR = 2  # time period to assess for still active
    STILL_O_THR = 2  # times to be active within STILL_T_THR to be still active
    # time periods into the past (history) to be newly active for computing dropped
    DROP_H_THR = 2
    # consecutive time periods into the past to have not been active for computing
    DROP_I_THR = 1

    act_param = [
        INT_THR,
        UW_DEG_THR,
        PAUSED_T_THR,
        CON_T_THR,
        CON_O_THR,
        EDGE_STR_THR,
        UW_THR_DEG_THR,
        VITAL_T_THR,
        VITAL_O_THR,
        STILL_T_THR,
        STILL_O_THR,
        DROP_H_THR,
        DROP_I_THR,
    ]

    int_mat = {
        DiscordActivity.Reply: np.zeros((acc_count, acc_count)),
        DiscordActivity.Mention: np.zeros((acc_count, acc_count)),
        DiscordActivity.Reaction: np.zeros((acc_count, acc_count)),
    }

    # `user_1` intracting with `user_2`
    int_mat[DiscordActivity.Reaction][0, 1] = 2

    activities = [
        DiscordActivity.Reaction,
        DiscordActivity.Mention,
        DiscordActivity.Reply,
    ]

    engagement = EngagementAssessment(
        activities=activities, activities_ignore_0_axis=[], activities_ignore_1_axis=[]
    )

    # the analytics
    for w_i in range(max_interval):
        # time window
        WINDOW_D = 7

        (_, *activity_dict) = engagement.compute(
            int_mat=int_mat,
            w_i=w_i,
            acc_names=acc_names,
            act_param=act_param,
            WINDOW_D=WINDOW_D,
            **activity_dict,
        )

        activity_dict = dict(zip(memberactivities, activity_dict))

        # zeroing all the activities on day 29
        # meaning we could have disengaged members on day (29 + 7) = 36
        # 14 is two periods
        if w_i == 28:
            int_mat[DiscordActivity.Reaction][0, 1] = 0

    print("all_active", activity_dict["all_active"])
    print("all_disengaged", activity_dict["all_disengaged"])

    assert activity_dict["all_disengaged"] == {
        "0": set(),
        "1": set(),
        "2": set(),
        "3": set(),
        "4": set(),
        "5": set(),
        "6": set(),
        "7": set(),
        "8": set(),
        "9": set(),
        "10": set(),
        "11": set(),
        "12": set(),
        "13": set(),
        "14": set(),
        "15": set(),
        "16": set(),
        "17": set(),
        "18": set(),
        "19": set(),
        "20": set(),
        "21": set(),
        "22": set(),
        "23": set(),
        "24": set(),
        "25": set(),
        "26": set(),
        "27": set(),
        "28": set(),
        "29": set(),
        "30": set(),
        "31": set(),
        "32": set(),
        "33": set(),
        "34": set(),
        "35": set(),
        "36": {"user1", "user0"},
        "37": {"user1", "user0"},
        "38": {"user1", "user0"},
        "39": {"user1", "user0"},
        "40": {"user1", "user0"},
        "41": {"user1", "user0"},
        "42": {"user1", "user0"},
        "43": {"user1", "user0"},
        "44": {"user1", "user0"},
        "45": {"user1", "user0"},
        "46": {"user1", "user0"},
        "47": {"user1", "user0"},
        "48": {"user1", "user0"},
        "49": {"user1", "user0"},
    }
