
from objects.object_enums import ResetReason
import alarms
import clock
import sims4.hash_util
import sims4.math
import sims4.resources
import zone_types
import sims4.tuning.tunable
from info import *

import sims4.log
with sims4.reload.protected(globals()):
    _reset_alarm_handles = {}

import services
import sims4.commands

#currently has chance of crashing game - not fully correctly implemented
@sims4.commands.Command('adopt',command_type=sims4.commands.CommandType.Live)
def simulate_adoption(first_name1='',last_name1='',_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output(first_name1+" "+last_name1+" is adopting...")
    for coll in services.get_adoption_service()._sim_infos.values():
        for item in coll:
            item =  services.get_adoption_service().convert_base_sim_info_to_full(item.sim_id)
            services.get_adoption_service().remove_sim_info(item)

            first_sim_info = services.sim_info_manager().get_sim_info_by_name(first_name1, last_name1)
            PregnancyTracker.initialize_sim_info(item,first_sim_info,None)

            return

#untested
@sims4.commands.Command('adoptascouple',command_type=sims4.commands.CommandType.Live)
def simulate_couple_adoption(first_name1='',last_name1='', first_name2='',last_name2='',_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output(first_name1+" "+last_name1+" is adopting...")
    for coll in services.get_adoption_service()._sim_infos.values():
        for item in coll:
            item =  services.get_adoption_service().convert_base_sim_info_to_full(item.sim_id)
            services.get_adoption_service().remove_sim_info(item)

            first_sim_info = services.sim_info_manager().get_sim_info_by_name(first_name1, last_name1)
            second_sim_info = services.sim_info_manager().get_sim_info_by_name(first_name2, last_name2)
            PregnancyTracker.initialize_sim_info(item,first_sim_info,second_sim_info)

            return
@sims4.commands.Command('forcepregnancy', command_type=sims4.commands.CommandType.Live)
def force_pregnancy(first_name1='', last_name1='', first_name2='', last_name2='',  _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    first_sim_info = services.sim_info_manager().get_sim_info_by_name(first_name1, last_name1)
    second_sim_info = services.sim_info_manager().get_sim_info_by_name(first_name2, last_name2)
    pregnancy_tracker = first_sim_info.pregnancy_tracker
    pregnancy_tracker.start_pregnancy(first_sim_info, second_sim_info)
    if pregnancy_tracker.is_pregnant:
        output("Pregnant!")
    else:
        output("Pregnancy Attempt Failed")
        return

    pregnancy_tracker.complete_pregnancy()
    pregnancy_tracker._create_and_name_offspring()
    pregnancy_tracker._show_npc_dialog()
    pregnancy_tracker.clear_pregnancy()
    pregnancy_tracker.clear_pregnancy_visuals()
@sims4.commands.Command('forceslowpregnancy', command_type=sims4.commands.CommandType.Live)
def force_slow_pregnancy(first_name1='', last_name1='', first_name2='', last_name2='',  _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    first_sim_info = services.sim_info_manager().get_sim_info_by_name(first_name1, last_name1)
    second_sim_info = services.sim_info_manager().get_sim_info_by_name(first_name2, last_name2)
    pregnancy_tracker = first_sim_info.pregnancy_tracker
    pregnancy_tracker.start_pregnancy(first_sim_info, second_sim_info)
    if pregnancy_tracker.is_pregnant:
        output("Pregnant!")
    else:
        output("Pregnancy Attempt Failed")
        return


def _remove_alarm_helper(*args):
    current_zone = services.current_zone()
    if current_zone in _reset_alarm_handles:
        alarms.cancel_alarm(_reset_alarm_handles[current_zone])
        del _reset_alarm_handles[current_zone]
        current_zone.unregister_callback(zone_types.ZoneState.SHUTDOWN_STARTED, _remove_alarm_helper)


def _apply_baby_chances(couples,_connection):
    output = sims4.commands.CheatOutput(_connection)
    output("Applying chances:")
    for couple in couples:
        baby = couple.have_baby()
        if baby is None:
            output("Couple: "+ couple.sim1.fullName + ", " + couple.sim2.fullName+" not having baby")
        else:
            output("Couple: "+ couple.sim1.fullName + ", " + couple.sim2.fullName+" had a baby")

    output("Done  iterating through all sims")

def getAllSims(_connection):
    output = sims4.commands.CheatOutput(_connection)
    # for each sim, get the couple they belong to, if they are in  1
    seen_sims = []  # contains sim_info objects
    couples = []  # contains CoupleInfo objects

    # get all sims, and iterate through  them
    for sim in services.sim_info_manager().get_all():
        if sim:
            if sim not in seen_sims:
                sim1 = SimInfo(sim)
                seen_sims.append(sim)
                if sim1 is not None:
                    if sim1.hasSpouse():
                        sim2 = SimInfo(sim1.getSpouse())
                        seen_sims.append(sim1.getSpouse())
                        couple = CoupleInfo(sim1, sim2)
                        output(str(couple))
                        couples.append(couple)
                    else:
                        output(str(sim1))
                else:
                    output("SimInfo  failed")

        else:
            output("Got None  from getAll")
    return seen_sims, couples
@sims4.commands.Command('runmod', command_type=sims4.commands.CommandType.Live)
def simulate_story_progression(enable:bool=True,  _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output("Running mod")
    _remove_alarm_helper()
    seen_sims, couples = getAllSims(_connection)

    if not enable:
        return

    def reset_helper(self):
        current_zone = services.current_zone()
        output("Interval elapse")
        _apply_baby_chances(couples,_connection)
        alarms.cancel_alarm(_reset_alarm_handles[current_zone])
        reset_time_span = clock.interval_in_sim_minutes(10)
        _reset_alarm_handles[current_zone] = alarms.add_alarm(simulate_story_progression,
                                                              reset_time_span, reset_helper)

    reset_time_span = clock.interval_in_sim_minutes(10)
    current_zone = services.current_zone()
    _reset_alarm_handles[current_zone] = alarms.add_alarm(simulate_story_progression,
                                                          reset_time_span, reset_helper)
    current_zone.register_callback(zone_types.ZoneState.SHUTDOWN_STARTED, _remove_alarm_helper)

