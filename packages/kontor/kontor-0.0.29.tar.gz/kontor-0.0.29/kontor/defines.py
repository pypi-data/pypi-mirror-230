#!/usr/bin/env python
import json
import logging
import socket
import time
from dataclasses import dataclass
from enum import Enum

MARKER_TRANSMISSION_START: str = "<TRANSMISSION_START>"
MARKER_TRANSMISSION_END: str = "<TRANSMISSION_END>"
MARKER_FILE_START: bytes = b"<FILE_START>"
MARKER_FILE_END: bytes = b"<FILE_END>"


class TransmissionType(str, Enum):
    UNKNOWN = "UNKNOWN"
    CLERK_READY = "CLERK_READY"
    APPLICANT_READY = "APPLICANT_READY"
    AUTH_REQUEST = "AUTH_REQUEST"
    AUTH_RESPONSE = "AUTH_RESPONSE"
    PROCEDURE_REQUEST = "PROCEDURE_REQUEST"
    PROCEDURE_RESPONSE = "PROCEDURE_RESPONSE"
    FILE_RECEIVING_RECEIPT = "FILE_RECEIVING_RECEIPT"
    PROCEDURE_RECEIPT = "PROCEDURE_RECEIPT"


class FileType(str, Enum):
    NONE = "NONE"
    SINGLE = "SINGLE"
    ARCHIVE = "ARCHIVE"


@dataclass
class ClerkReadyMessage:
    type: TransmissionType = TransmissionType.CLERK_READY
    applicant_ip: str = ""
    applicant_port: int = 0


@dataclass
class ApplicantReadyMessage:
    type: TransmissionType = TransmissionType.APPLICANT_READY


@dataclass
class AuthRequestMessage:
    type: TransmissionType = TransmissionType.AUTH_REQUEST
    username: str = ""
    password_hash: str = ""


@dataclass
class AuthResponseMessage:
    type: TransmissionType = TransmissionType.AUTH_RESPONSE
    is_authenticated: bool = False
    message: str = ""


@dataclass
class ProcedureRequestMessage:
    type: TransmissionType = TransmissionType.PROCEDURE_REQUEST
    procedure: str = ""
    file_type: FileType = FileType.NONE
    file_name: str = ""
    file_size_bytes: int = 0
    file_crc32: str = ""


@dataclass
class ProcedureResponseMessage:
    type: TransmissionType = TransmissionType.PROCEDURE_RESPONSE
    is_ready_for_procedure: bool = False
    message: str = ""


@dataclass
class FileReceivingReceiptMessage:
    type: TransmissionType = TransmissionType.FILE_RECEIVING_RECEIPT
    is_received_correctly: bool = False
    message: str = ""


@dataclass
class ProcedureReceiptMessage:
    type: TransmissionType = TransmissionType.PROCEDURE_RECEIPT
    is_processed_correctly: bool = False
    message: str = ""
    file_size_bytes: int = 0
    file_crc32: str = ""


class ConnectionBrokenException(Exception):
    pass


class ConnectionTimeoutException(Exception):
    pass


class InvalidMessageFormatException(Exception):
    pass


class UnexpectedMessageException(Exception):
    pass


class AuthenticationFailureException(Exception):
    pass


class ProcedureApprovalException(Exception):
    pass


class ProcedureExecutionException(Exception):
    pass


class ProcedureAlreadyPresentException(Exception):
    pass


class FileTransmissionException(Exception):
    pass


class EmptyFileListException(Exception):
    pass


class MissingWorkingDirectoryException(Exception):
    pass


class ServerStartTimeoutException(Exception):
    pass


def send_message(connection: socket.socket, address, message: dict):
    """
    Sends file through provided connection.

    Parameters:
        connection : socket.socket
            connection through where to send message
        address : tuple
            connection address for logging
        message : dict
            message to be sent
    """
    logging.debug("%s: Sending message: %s.", address, message)
    json_data_str = json.dumps(message)
    connection.sendall(
        bytes(
            MARKER_TRANSMISSION_START + json_data_str + MARKER_TRANSMISSION_END,
            encoding="utf-8",
        )
    )


def wait_and_receive_response(connection: socket.socket, address) -> dict:
    """
    Receives message that came from connection.
    Raises socket.timeout exception in case of timeout.

    Parameters:
        connection : socket.socket
            connection from where to expect message
        address : tuple
            connection address for logging

    Returns:
        message : dict
            received message of any type as dict
    """
    logging.debug("%s: Waiting for response.", address)

    raw_data = ""
    message = dict()
    is_message_received = False
    while not is_message_received:
        raw_data += connection.recv(1).decode("utf-8")
        if len(raw_data) == 0:
            # socket returns 0 when other party calls socket.close().
            raise ConnectionBrokenException(f"{address}: Connected party disconnected.")

        if (
            raw_data.find(MARKER_TRANSMISSION_START) != -1
            and raw_data.find(MARKER_TRANSMISSION_END) != -1
        ):
            message_start_marker_index = raw_data.find(MARKER_TRANSMISSION_START) + len(
                MARKER_TRANSMISSION_START
            )
            message_end_marker_index = raw_data.find(MARKER_TRANSMISSION_END)

            message_data = raw_data[message_start_marker_index:message_end_marker_index]
            message = json.loads(message_data)
            logging.debug("%s: Received message: %s.", address, message)

            message_end_index = message_end_marker_index + len(MARKER_TRANSMISSION_END)
            if len(raw_data) <= message_end_index:
                raw_data = ""
            else:
                raw_data = raw_data[message_end_index:]

            is_message_received = True

    return message


def send_file(connection: socket.socket, address, file: bytes):
    """
    Sends file through provided connection.

    Parameters:
        connection : socket.socket
            connection through where to send file
        address : tuple
            connection address for logging
        file : bytes
            file to be sent
    """
    logging.debug("%s: Sending file.", address)
    connection.send(MARKER_FILE_START)
    connection.sendall(file)
    connection.send(MARKER_FILE_END)


def wait_and_receive_file(
    connection: socket.socket, address, corrected_file_path: str, file_size_bytes: int
):
    """
    Waits for the file to arrive and saves to specified path.
    Raises socket.timeout exception in case of timeout.

    Parameters:
        connection : socket.socket
            connection from where to expect file
        address : tuple
            connection address for logging
        corrected_file_path : str
            path where to save received file
        file_size_bytes : int
            expected file size in bytes
    """
    with open(corrected_file_path, "wb") as processed_file:
        file_received_fully = False
        received_bytes = 0
        previous_percents = 0
        chunk_size_bytes = 256 * 1024

        file_start_time = time.time()
        while not file_received_fully:
            data = connection.recv(chunk_size_bytes)
            if len(data) == 0:
                break

            file_start_marker_length = len(MARKER_FILE_START)
            if data[:file_start_marker_length] == MARKER_FILE_START:
                data = data[file_start_marker_length:]

            file_end_marker_length = len(MARKER_FILE_END)
            if data[-file_end_marker_length:] == MARKER_FILE_END:
                file_received_fully = True
                data = data[:-file_end_marker_length]

            received_bytes += len(data)
            received_percents = int(100 / file_size_bytes * received_bytes)

            if received_percents % 10 == 0 and previous_percents != received_percents:
                previous_percents = received_percents
                logging.info(
                    "%s: Receiving file, %d%% (%d / %d).",
                    address,
                    received_percents,
                    received_bytes,
                    file_size_bytes,
                )

            processed_file.write(data)

        file_upload_time = time.time() - file_start_time
        logging.info("%s: File receiving time is %.2f seconds.", address, file_upload_time)
