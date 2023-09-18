import sys
import os
sys.path.append(os.getcwd())
from redundancy_solver import *
import unittest
from datetime import datetime
import string
import random



class RedundancySolverTest(unittest.TestCase):
    def test_merge_experiences_general(self):
        institution="apple"
        specialization="farmer"
        experience_0=GeneralExperience(Institution=institution, Specialization=specialization)
        experience_1=GeneralExperience(Institution=institution, Specialization=specialization)
        result_experience=merge_experiences(experience_0, experience_1, summary_name=LSA)
        self.assertEqual(result_experience.Institution, institution)
        self.assertEqual(result_experience.Specialization, specialization)

    def test_merge_experiences_education(self):
        institution="oxford university"
        specialization="history"
        degree="phd"
        education_0=EducationExperience(Degree=degree, Institution=institution, Specialization=specialization)
        education_1=EducationExperience(Degree=degree, Institution=institution, Specialization=specialization)
        result_education=merge_experiences(education_0, education_1, summary_name=LSA)
        self.assertEqual(result_education.Institution, institution)
        self.assertEqual(result_education.Specialization, specialization)
        self.assertEqual(result_education.Degree, degree)

    def test_merge_experiences_exception(self):
        institution="oxford university"
        specialization="history"
        degree="phd"
        experience_0=GeneralExperience(Institution="microsoft", Specialization="salesperson")
        education_0=EducationExperience(Degree=degree, Institution=institution, Specialization=specialization)
        with self.assertRaises(Exception):
            merge_experiences(experience_0, education_0)


    def test_merge_general_experience_list(self):
        general_experience_list=[GeneralExperience(Institution="apple", Specialization="farmer") for _ in range(3)]
        result_general_experience_list= merge_general_experience_list(general_experience_list, summary_name=LSA)
        self.assertEqual(len(result_general_experience_list),1)
    
    def test_merge_general_experience_list_not_eq(self):
        general_experience_list=[GeneralExperience(Institution="apple", Specialization="farmer"), 
                                 GeneralExperience(Institution="netflix", Specialization="watcher")]
        result_general_experience_list= merge_general_experience_list(general_experience_list, summary_name=LSA)
        self.assertEqual(len(result_general_experience_list),2)

    def test_merge_redundant_candidates_different(self):
        candidate_list=[Candidate(Name=''.join(random.choices(string.ascii_lowercase +
                             string.digits, k=10))) for x in range(3)]
        result_candidate_list=merge_redundant_candidates(candidate_list, LSA)
        self.assertEqual(len(result_candidate_list),3)

    def test_merge_redundant_candidates_by_sources(self):
        source_list=["linkedin.com/joebiden", "indeed.com/joebiden"]
        candidate_list=[Candidate(Name=''.join(random.choices(string.ascii_lowercase +
                             string.digits, k=10)), Sources=source_list) for x in range(3) ]
        result_candidate_list=merge_redundant_candidates(candidate_list, LSA)
        self.assertEqual(len(result_candidate_list),1)

    def test_merge_redundant_candidates_by_summaries(self):
        name_list=['joe biden', 'joseph biden']
        candidate_list=[Candidate(Name=name_list[x]) for x in range(2)]
        result_candidate_list=merge_redundant_candidates(candidate_list, LSA)
        self.assertEqual(len(result_candidate_list),2)

        work_experience_list=[WorkExperience(Institution="United States", Specialization="President"),
                              WorkExperience(Institution="Congress", Specialization="Senator")]
        candidate_list=[
            Candidate(Name=name_list[x], WorkExperienceList=work_experience_list)
            for x in range(2)]
        result_candidate_list=merge_redundant_candidates(candidate_list, LSA)
        self.assertEqual(len(result_candidate_list),1)


if __name__ == '__main__':
    unittest.main()
