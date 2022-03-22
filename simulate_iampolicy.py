#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  simulate_iampolicy.py
#  ======
#  Copyright (C) 2022 n.fujita
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
from __future__ import print_function
import sys
import argparse
import json
import boto3
import csv

MaxItems = 100

# ---------------------------
# Functions
# ---------------------------
def get_args():
    parser = argparse.ArgumentParser(
        description='Simulate policy by IAM Policy Simulator')

    parser.add_argument('-P', '--profile',
        action='store',
        default='',
        type=str,
        required=False,
        help='Specify the AWS Profile.'
    )

    parser.add_argument('-c', '--csv',
        action='store_true',
        required=False,
        help='Output in CSV format.'
    )

    parser.add_argument('-p', '--policy-source-arn',
        action='store',
        default='NA',
        type=str,
        required=True,
        help='Specify the ARN of a user, group, or role whose policies you want to include in the simulation.'
    )

    parser.add_argument('-a','--action-list-file',
        action='store',
        default='NA',
        type=str,
        required=True,
        help='Specifies the file path of the name list of API operations to evaluate in the simulation written in JSON format.'
    )
    return( parser.parse_args() )

def get_session(profile):
    ret = None
    if profile != '':
        ret = boto3.session.Session(
            profile_name = profile
        )
    else:
        ret = boto3.session.Session()

    return ret


# ---------------------------
# Main function
# ---------------------------
def main():

    # Initialize
    args = get_args()

    #Read List of Action Name
    ActionList = json.load( open( args.action_list_file, 'r' ) )

    #Similate iam policy
    session = get_session(args.profile)
    client = session.client('iam')

    IsTruncated = False
    Marker = ''
    results = []
    while True:
        #Call API
        if IsTruncated:
            ret = client.simulate_principal_policy(
                PolicySourceArn = args.policy_source_arn,
                ActionNames     = ActionList['Action'],
                MaxItems        = MaxItems,
                Marker          = Marker
            )
        else:
            ret = client.simulate_principal_policy(
                PolicySourceArn = args.policy_source_arn,
                ActionNames     = ActionList['Action'],
                MaxItems        = MaxItems
            )
        
        #Get results
        for i in ret['EvaluationResults']:
            item = {key: value for key, value in i.items() if key == 'EvalActionName' or key == 'EvalDecision' }
            results.append(item)

        #Check
        if ret['IsTruncated']:
            IsTruncated = True
            Marker      = ret['Marker']
        else:
            break

    #Output results
    if args.csv:
        writer = csv.writer(sys.stdout)
        writer.writerow(['EvalActionName', 'EvalDecision'])
        for i in results:
            j = [ value for key, value in i.items() ]
            writer.writerow(j)
    else:
        json.dump(results, sys.stdout, ensure_ascii=False, indent=2)

    # Finish
    return

if __name__ == "__main__":
    sys.exit(main())