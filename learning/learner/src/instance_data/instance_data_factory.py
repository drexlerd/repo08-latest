import logging
import dlplan
import os

from learner.src.instance_data.instance_data import InstanceData
from learner.src.util.command import create_experiment_workspace

class InstanceDataFactory:
    def make_instance_datas(self, config, domain_data):
        cwd = os.getcwd()
        instance_datas = []
        for instance_information in config.instance_informations:
            logging.info(f"Constructing InstanceData for filename {instance_information.filename}")
            create_experiment_workspace(instance_information.workspace, False)
            # change working directory to put planner output files in correct directory
            os.chdir(instance_information.workspace)
            state_space = dlplan.generate_state_space(str(domain_data.domain_filename), str(instance_information.filename), domain_data.vocabulary_info, len(instance_datas))
            if len(state_space.get_states()) > config.max_states_per_instance:
                continue
            goal_distances = state_space.compute_goal_distances()
            if goal_distances.get(state_space.get_initial_state_index(), None) is None:
                print("Unsolvable.")
                continue
            if set(state_space.get_states().keys()) == set(state_space.get_goal_state_indices()):
                print("Trivially solvable.")
                continue
            else:
                print("Num states:", len(state_space.get_states()))
                instance_data = InstanceData(len(instance_datas), domain_data, dlplan.DenotationsCaches(), instance_information)
                instance_data.set_state_space(state_space, create_dump=True)
                instance_data.set_goal_distances(goal_distances)
                instance_data.initial_s_idxs = [state_space.get_initial_state_index(),]
                instance_datas.append(instance_data)
        # Sort the instances according to size and fix the indices afterwards
        instance_datas = sorted(instance_datas, key=lambda x : len(x.state_space.get_states()))
        for instance_idx, instance_data in enumerate(instance_datas):
            instance_data.id = instance_idx
            instance_data.state_space.get_instance_info().set_index(instance_idx)
        # change back working directory
        os.chdir(cwd)
        return instance_datas
