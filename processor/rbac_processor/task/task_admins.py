# Copyright 2017 Intel Corporation
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
# -----------------------------------------------------------------------------

from sawtooth_sdk.processor.exceptions import InvalidTransaction

from rbac_addressing import addresser

from rbac_processor.common import no_open_proposal
from rbac_processor.task.common import handle_propose_state_set
from rbac_processor.task.common import handle_confirm_add
from rbac_processor.task.common import handle_reject
from rbac_processor.task.common import validate_task_rel_proposal
from rbac_processor.task.common import validate_task_rel_del_proposal
from rbac_processor.task.common import validate_task_admin_or_owner
from rbac_processor.protobuf import proposal_state_pb2
from rbac_processor.protobuf import task_transaction_pb2


def apply_propose(header, payload, state):
    """Apply the ProposeAddTaskAdmins transaction.

    Args:
        header (TransactionHeader): The protobuf TransactionHeader.
        payload (RBACPayload): The protobuf RBACPayload.
        state (Context): The class that handles state gets and sets.

    Raises:
        InvalidTransaction:
            - The transaction is invalid.
    """

    propose = task_transaction_pb2.ProposeAddTaskAdmin()
    propose.ParseFromString(payload.content)

    task_admins_address = addresser.make_task_admins_address(
        task_id=propose.task_id,
        user_id=propose.user_id)

    proposal_address = addresser.make_proposal_address(
        propose.task_id,
        propose.user_id)

    state_entries = validate_task_rel_proposal(
        header=header,
        propose=propose,
        rel_address=task_admins_address,
        state=state)

    if not no_open_proposal(
            state_entries=state_entries,
            object_id=propose.task_id,
            related_id=propose.user_id,
            proposal_address=proposal_address,
            proposal_type=proposal_state_pb2.Proposal.ADD_TASK_ADMINS):
        raise InvalidTransaction(
            "There is already an open proposal for ADD_TASK_ADMINS "
            "with task id {} and user id {}".format(propose.task_id,
                                                    propose.user_id))

    handle_propose_state_set(
        state_entries=state_entries,
        header=header,
        payload=propose,
        address=proposal_address,
        proposal_type=proposal_state_pb2.Proposal.ADD_TASK_ADMINS,
        state=state)


def apply_propose_remove(header, payload, state):
    """Apply the ProposeRemoveTaskAdmins transaction.

    Args:
        header (TransactionHeader): The protobuf TransactionHeader.
        payload (RBACPayload): The protobuf RBACPayload.
        state (Context): The class that handles state gets and sets.

    Raises
        InvalidTransaction:
            - The transaction is invalid.

    """

    propose_payload = task_transaction_pb2.ProposeRemoveTaskAdmin()
    propose_payload.ParseFromString(payload.content)

    task_admins_address = addresser.make_task_admins_address(
        task_id=propose_payload.task_id,
        user_id=propose_payload.user_id)

    proposal_address = addresser.make_proposal_address(
        propose_payload.task_id,
        propose_payload.user_id)

    state_entries = validate_task_rel_del_proposal(
        header=header,
        propose=propose_payload,
        rel_address=task_admins_address,
        state=state)

    if not no_open_proposal(
            state_entries=state_entries,
            object_id=propose_payload.task_id,
            related_id=propose_payload.user_id,
            proposal_address=proposal_address,
            proposal_type=proposal_state_pb2.Proposal.REMOVE_TASK_ADMINS):
        raise InvalidTransaction(
            "There is already an open proposal for REMOVE_TASK_ADMINS "
            "with task id {} and user id {}".format(propose_payload.task_id,
                                                    propose_payload.user_id))
    handle_propose_state_set(
        state_entries=state_entries,
        header=header,
        payload=propose_payload,
        address=proposal_address,
        proposal_type=proposal_state_pb2.Proposal.REMOVE_TASK_ADMINS,
        state=state)


def apply_confirm(header, payload, state):
    confirm_payload = task_transaction_pb2.ConfirmAddTaskAdmin()
    confirm_payload.ParseFromString(payload.content)

    task_admins_address = addresser.make_task_admins_address(
        task_id=confirm_payload.task_id,
        user_id=confirm_payload.user_id)

    txn_signer_admin_address = addresser.make_task_admins_address(
        task_id=confirm_payload.task_id,
        user_id=header.signer_public_key)

    state_entries = validate_task_admin_or_owner(
        header=header,
        confirm=confirm_payload,
        txn_signer_rel_address=txn_signer_admin_address,
        state=state)

    handle_confirm_add(
        state_entries=state_entries,
        header=header,
        confirm=confirm_payload,
        task_rel_address=task_admins_address,
        state=state)


def apply_reject(header, payload, state):
    reject_payload = task_transaction_pb2.RejectAddTaskAdmin()
    reject_payload.ParseFromString(payload.content)

    txn_signer_admin_address = addresser.make_task_admins_address(
        task_id=reject_payload.task_id,
        user_id=header.signer_public_key)

    state_entries = validate_task_admin_or_owner(
        header,
        reject_payload,
        txn_signer_admin_address,
        state)

    handle_reject(state_entries, header, reject_payload, state)
