#!/usr/bin/env python
# Copyright 2023 AstroLab Software
# Author: Julien Peloton
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" Kafka consumer to listen and archive Fink streams from the data transfer service """
import sys
import os
import io
import glob
import json
import shutil
import argparse

import pyarrow as pa
import pyarrow.parquet as pq
import fastavro
import confluent_kafka

import numpy as np
import pandas as pd

from fink_client.consumer import return_offsets

from fink_client.configuration import load_credentials

def get_schema(kafka_config, topic, maxtimeout):
    """
    """
    # Instantiate a consumer
    consumer_schema = confluent_kafka.Consumer(kafka_config)

    # Subscribe to schema topic
    topics = ['{}_schema'.format(topic)]
    consumer_schema.subscribe(topics)

    # Poll
    msg = consumer_schema.poll(maxtimeout)
    if msg is not None:
        schema = fastavro.schema.parse_schema(json.loads(msg.key()))
    else:
        schema = None

    consumer_schema.close()

    return schema

def my_assign(consumer, partitions):
    """
    """
    for p in partitions:
        p.offset = 0
    # print('assign', partitions)
    consumer.assign(partitions)

def main():
    """ """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-topic', type=str, default='.',
        help="Topic name for the stream that contains the data.")
    parser.add_argument(
        '-limit', type=int, default=None,
        help="If specified, download only `limit` alerts from the stream. Default is None, that is download all alerts.")
    parser.add_argument(
        '-outdir', type=str, default='.',
        help="Folder to store incoming alerts. It will be created if it does not exist.")
    parser.add_argument(
        '-partitionby', type=str, default='time',
        help="Partition data by `time` (year=YYYY/month=MM/day=DD), or `finkclass` (finkclass=CLASS), or `tnsclass` (tnsclass=CLASS). `classId` is also available for ELASTiCC data. Default is time.")
    parser.add_argument(
        '-batchsize', type=int, default=1000,
        help="Maximum number of alert within the `maxtimeout` (see conf). Default is 1000 alerts.")
    parser.add_argument(
        '--restart_from_beginning', action='store_true',
        help="If specified, restart downloading from the 1st alert in the stream. Default is False.")
    parser.add_argument(
        '--list_offsets', action='store_true',
        help="If specified, list the current offset commited, and the lag (remaining alerts to poll), and exit.")
    parser.add_argument(
        '--verbose', action='store_true',
        help="If specified, print on screen information about the consuming.")
    args = parser.parse_args(None)

    if args.partitionby not in ['time', 'finkclass', 'tnsclass', 'classId']:
        print("{} is an unknown partitioning. `-partitionby` should be in ['time', 'finkclass', 'tnsclass', 'classId']".format(args.partitionby))
        sys.exit()

    # load user configuration
    conf = load_credentials()

    group_id = conf['group_id']
    # if args.restart_from_beginning:
    #     # resetting the group ID acts as a new consumer
    #     group_id = conf['group_id'] + '_{}'.format(np.random.randint(1e6))
    # else:
    #     group_id = conf['group_id']

    kafka_config = {
        'bootstrap.servers': conf['servers'],
        'group.id': group_id,
        "auto.offset.reset": "earliest"
    }

    if conf['password'] is not None:
        kafka_config['password'] = conf['password']

    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir, exist_ok=True)

    # Time to wait before polling again if no alerts
    maxtimeout = conf['maxtimeout']

    if (args.limit is not None) and (args.limit < args.batchsize):
        args.batchsize = args.limit

    schema = get_schema(kafka_config, args.topic, maxtimeout)
    if schema is None:
        #TBD: raise error
        print('No schema found -- wait a few seconds and relaunch. If the error persists, maybe the queue is empty.')

    # Instantiate a consumer
    consumer = confluent_kafka.Consumer(kafka_config)

    # Subscribe to schema topic
    topics = ['{}'.format(args.topic)]

    if args.restart_from_beginning:
        consumer.subscribe(topics, on_assign=my_assign)
    else:
        consumer.subscribe(topics)

    # infinite loop
    maxpoll = args.limit if args.limit is not None else 1e10
    parts = []
    try:
        poll_number = 0
        while poll_number < maxpoll:
            msgs = consumer.consume(args.batchsize, maxtimeout)
            # Decode the message
            if msgs is not None:
                pdf = pd.DataFrame.from_records(
                    [fastavro.schemaless_reader(io.BytesIO(msg.value()), schema) for msg in msgs],
                )
                if pdf.empty:
                    print("%-50s  %9s  %9s" % ("Topic [Partition]", "Committed", "Lag"))
                    print("=" * 72)
                    initial_offset, lag = return_offsets(consumer, args.topic, waitfor=1, verbose=True)
                    print('No alerts the last {} seconds ({} polled)... Exiting'.format(maxtimeout, poll_number))
                    break

                [parts.append(i.partition()) for i in msgs]

                # known mismatches between partitions
                # see https://github.com/astrolabsoftware/fink-client/issues/165
                if 'cats_broad_max_prob' in pdf.columns:
                    pdf['cats_broad_max_prob'] = pdf['cats_broad_max_prob'].astype('float')

                if 'cats_broad_class' in pdf.columns:
                    pdf['cats_broad_class'] = pdf['cats_broad_class'].astype('float')

                if 'tracklet' in pdf.columns:
                    pdf['tracklet'] = pdf['tracklet'].astype('str')

                # if 'jd' in pdf.columns:
                #     # create columns year, month, day

                table = pa.Table.from_pandas(pdf)

                if poll_number == 0:
                    table_schema = table.schema

                if args.partitionby == 'time':
                    partitioning = ['year', 'month', 'day']
                elif args.partitionby == 'finkclass':
                    partitioning = ['finkclass']
                elif args.partitionby == 'tnsclass':
                    partitioning = ['tnsclass']
                elif args.partitionby == 'classId':
                    partitioning = ['classId']

                try:
                    pq.write_to_dataset(
                        table,
                        args.outdir,
                        schema=table_schema,
                        basename_template='part-{{i}}-{}.parquet'.format(poll_number),
                        partition_cols=partitioning,
                        existing_data_behavior='overwrite_or_ignore'
                    )
                except pa.lib.ArrowTypeError:
                    print('Schema mismatch detected')
                    table_schema_ = table.schema
                    pq.write_to_dataset(
                        table,
                        args.outdir,
                        schema=table_schema_,
                        basename_template='part-{{i}}-{}.parquet'.format(poll_number),
                        partition_cols=partitioning,
                        existing_data_behavior='overwrite_or_ignore'
                    )

                if args.verbose:
                    if poll_number == 0:
                        print("%-50s  %9s  %9s" % ("Topic [Partition]", "Committed", "Lag"))
                        print("=" * 72)
                        initial_offset, lag = return_offsets(consumer, args.topic, waitfor=5, verbose=True)
                    elif lag - poll_number >= 0:
                        # TBD get the last offset commited, and add it
                        print("%-50s  %9s  %9s" % (
                            "", initial_offset + poll_number, lag - poll_number))
                    else:
                        print('No more alerts found ({} polled)'.format(initial_offset + lag))
                        break
                poll_number += len(msgs)
            else:
                print("%-50s  %9s  %9s" % ("Topic [Partition]", "Committed", "Lag"))
                print("=" * 72)
                initial_offset, lag = return_offsets(consumer, args.topic, waitfor=5, verbose=True)
                print('No alerts the last {} seconds ({} polled)'.format(maxtimeout, poll_number))
    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')
    finally:
        consumer.close()

    print(parts)

    # remove empty partition
    list_of_dirs = glob.glob(os.path.join(args.outdir, '*'))
    for d_ in list_of_dirs:
        if '__HIVE_DEFAULT_PARTITION__' in d_:
            print('Removing empty partition: {}'.format(d_))
            shutil.rmtree(d_)


if __name__ == "__main__":
    main()
