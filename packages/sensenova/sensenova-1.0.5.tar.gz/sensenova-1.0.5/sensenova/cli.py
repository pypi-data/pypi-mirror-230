import sys
from argparse import ArgumentParser

import sensenova.cli
from sensenova.util import fine_tunes_hyperparams, finetune_completions_option_params, fine_tune_lora_params
from sensenova.validators import (
    apply_necessary_remediation,
    apply_processors,
    get_processors,
    read_any_format,
    write_out_file,
)
from sensenova.upload_progress import BufferReader


class KnowledgeBase:
    @classmethod
    def create(cls, args):
        resp = sensenova.KnowledgeBase.create(
            description=args.description,
            files=args.files
        )
        print(resp)

    @classmethod
    def add_file(cls, args):
        add_resp = sensenova.KnowledgeBase.add_file(id=args.id, description=args.description)
        with open(args.file, "rb") as file_reader:
            buffer_reader = BufferReader(file_reader.read(), desc="Upload progress")
        resp = sensenova.KnowledgeBase.upload_file(
            aoss_url=add_resp["url"],
            file=buffer_reader
        )
        print(resp)

    @classmethod
    def get(cls, args):
        resp = sensenova.KnowledgeBase.retrieve(id=args.id)
        print(resp)

    @classmethod
    def delete(cls, args):
        resp = sensenova.KnowledgeBase.delete(args.id)
        print(resp)

    @classmethod
    def list(cls, args):
        resp = sensenova.KnowledgeBase.list()
        print(resp)

    @classmethod
    def download(cls, args):
        resp = sensenova.KnowledgeBase.download(id=args.id, file_id=args.file_id)
        print(resp.decode("utf-8"))

    @classmethod
    def delete_file(cls, args):
        resp = sensenova.KnowledgeBase.delete_file(args.id, args.file_id)
        print(resp)

    @classmethod
    def update(cls, args):
        resp = sensenova.KnowledgeBase.update(sid=args.id, description=args.description, files=args.files)
        print(resp)


class Dataset:
    @classmethod
    def create(cls, args):
        resp = sensenova.Dataset.create(
            description=args.description,
            files=args.files,
        )
        print(resp)


    @classmethod
    def update(cls, args):
        resp = sensenova.Dataset.update(
            sid=args.id,
            description=args.description,
            files=args.files
        )
        print(resp)

    @classmethod
    def add_file(cls, args):
        add_resp = sensenova.Dataset.add_file(id=args.id, description=args.description)
        with open(args.file, "rb") as file_reader:
            buffer_reader = BufferReader(file_reader.read(), desc="Upload progress")
        resp = sensenova.Dataset.upload_file(
            aoss_url=add_resp["url"],
            file=buffer_reader
        )
        print(resp)

    @classmethod
    def get(cls, args):
        resp = sensenova.Dataset.retrieve(id=args.id)
        print(resp)

    @classmethod
    def delete(cls, args):
        resp = sensenova.Dataset.delete(args.id)
        print(resp)

    @classmethod
    def list(cls, args):
        resp = sensenova.Dataset.list()
        print(resp)

    @classmethod
    def download(cls, args):
        resp = sensenova.Dataset.download(id=args.id, file_id=args.file_id)
        print(resp.decode("utf-8"))


class Model:
    @classmethod
    def get(cls, args):
        resp = sensenova.Model.retrieve(id=args.id)
        print(resp)

    @classmethod
    def delete(cls, args):
        resp = sensenova.Model.delete(args.id)
        print(resp)

    @classmethod
    def list(cls, args):
        resp = sensenova.Model.list()
        print(resp)


class Serving:
    @classmethod
    def list(cls, args):
        resp = sensenova.Serving.list()
        print(resp)

    @classmethod
    def create(cls, args):
        create_args = {
            "model": args.model,
            "config": {
                "run_time": args.run_time
            }
        }
        resp = sensenova.Serving.create(**create_args)
        print(resp)

    @classmethod
    def get(cls, args):
        resp = sensenova.Serving.retrieve(id=args.id)
        print(resp)

    @classmethod
    def delete(cls, args):
        resp = sensenova.Serving.delete(args.id)
        print(resp)

    @classmethod
    def cancel(cls, args):
        resp = sensenova.Serving.cancel(id=args.id)
        print(resp)

    @classmethod
    def relaunch(cls, args):
        resp = sensenova.Serving.relaunch(id=args.id)
        print(resp)


class ChatCompletion:
    @classmethod
    def create(cls, args):
        messages = [
            {"role": role, "content": content} for role, content in args.message
        ]
        created_args = {
            "messages": messages
        }
        for param in (
            "model",
            "know_ids",
            "temperature",
            "top_p",
            "max_new_tokens",
            "repetition_penalty",
            "stream",
            "user",
        ):
            attr = getattr(args, param)
            if attr is not None:
                created_args[param] = attr

        resp = sensenova.ChatCompletion.create(
            **created_args
        )

        if not args.stream:
            resp = [resp]

        for part in resp:
            choices = part['data']["choices"]
            for c_idx, c in enumerate(choices):
                if len(choices) > 1:
                    sys.stdout.write("===== Chat Completion {} =====\n".format(c_idx))
                if args.stream:
                    delta = c.get("delta")
                    if delta:
                        sys.stdout.write(delta)
                else:
                    sys.stdout.write(c["message"])
                    if len(choices) > 1:  # not in streams
                        sys.stdout.write("\n")
                sys.stdout.flush()
        print()


class FinetuneCompletion:
    @classmethod
    def create(cls, args):
        created_args = {
            "text": args.text,
            "model_id": args.model_id,
            "stream": args.stream
        }

        for param in finetune_completions_option_params():
            attr = getattr(args, param[0])

            if attr is not None:
                if param[2]:
                    attr = eval(attr)
                created_args[param[0]] = attr

        resp = sensenova.FinetuneCompletion.create(**created_args)

        if not args.stream:
            resp = [resp]

        for part in resp:
            content = part['answer']
            if content:
                sys.stdout.write(content)
            sys.stdout.flush()


class FineTune:
    @classmethod
    def list(cls, args):
        resp = sensenova.FineTune.list()
        print(resp)

    @classmethod
    def create(cls, args):
        create_args = {
            "model": args.model,
            "training_file": args.training_file,
            "suffix": args.suffix
        }
        training = {}
        lora = {}
        params = fine_tunes_hyperparams()
        lora_params = fine_tune_lora_params()
        for param in params:
            attr = getattr(args, param[0])
            if attr is not None:
                if param[2]:
                    attr = eval(attr)
                if param in lora_params:
                    lora[param[0]] = attr
                else:
                    training[param[0]] = attr
        if len(lora.keys()) > 0:
            training['lora'] = lora
        create_args["hyperparams"] = {
            "training": training
        }
        resp = sensenova.FineTune.create(**create_args)
        print(resp)

    @classmethod
    def get(cls, args):
        resp = sensenova.FineTune.retrieve(id=args.id)
        print(resp)

    @classmethod
    def delete(cls, args):
        resp = sensenova.FineTune.delete(args.id)
        print(resp)

    @classmethod
    def cancel(cls, args):
        resp = sensenova.FineTune.cancel(id=args.id)
        print(resp)

    @classmethod
    def prepare_data(cls, args):
        sys.stdout.write("Analyzing...\n")
        fname = args.file
        metas, remediation = read_any_format(fname)
        apply_necessary_remediation(None, remediation)
        processors = get_processors()

        apply_processors(
            metas,
            fname,
            processors,
            write_out_file_func=write_out_file
        )


class File:
    @classmethod
    def list(cls, args):
        resp = sensenova.File.list()
        print(resp)

    @classmethod
    def get(cls, args):
        resp = sensenova.File.retrieve(args.id)
        print(resp)

    @classmethod
    def delete(cls, args):
        resp = sensenova.File.delete(args.id)
        print(resp)

    @classmethod
    def download(cls, args):
        resp = sensenova.File.download(id=args.id)
        print(resp.decode("utf-8"))

    @classmethod
    def create(cls, args):
        with open(args.file, "rb") as file_reader:
            buffer_reader = BufferReader(file_reader.read(), desc="Upload progress")
            resp = sensenova.File.create(
                file=buffer_reader,
                scheme=args.scheme,
                description=args.description
            )
            print(resp)


class ChatSession:
    @classmethod
    def create(cls, args):
        created_args = {
            "system_prompt": []
        }
        if args and args.prompts:
            system_prompt = [
                {"role": role, "content": content} for role, content in args.prompts
            ]
            created_args["system_prompt"] = system_prompt
            print(created_args)
        resp = sensenova.ChatSession.create(
            **created_args
        )
        print(resp)


class ChatConversation:
    @classmethod
    def create(cls, args):
        created_args = {}
        for param in (
                "model",
                "know_ids",
                "action",
                "content",
                "session_id",
                "stream"
        ):
            attr = getattr(args, param)
            if attr is not None:
                created_args[param] = attr

        resp = sensenova.ChatConversation.create(
            **created_args
        )

        if not args.stream:
            resp = [resp]
        # {"data":{"delta":"","finish_reason":"stop","session_id":"55b1f0815c76000","turn_id":"55b6dc0b62a3000_1","usage":{"prompt_tokens":11,"completion_tokens":17,"total_tokens":28}},"status":{"code":0,"message":"OK"}}
        for part in resp:
            data = part['data']
            if args.stream:
                delta = data["delta"]
                if delta:
                    sys.stdout.write(delta)
            else:
                sys.stdout.write(data["message"])
            sys.stdout.flush()
        print()


def tools_register(parser):
    subparsers = parser.add_subparsers(
        title="Tools", help="Convenience client side tools"
    )

    def help(args):
        parser.print_help()

    parser.set_defaults(func=help)

    sub = subparsers.add_parser("fine_tunes.prepare_data")
    sub.add_argument(
        "-f",
        "--file",
        required=True,
        help="Json file contains a data list, each data contains three fields instruction, input, output"
             "This should be the local file path.",
    )
    sub.set_defaults(func=FineTune.prepare_data)


def api_register(parser: ArgumentParser):
    subparsers = parser.add_subparsers(help="All API subcommands")

    def help(args):
        parser.print_help()

    parser.set_defaults(func=help)

    # knowledge-bases
    sub = subparsers.add_parser("knowledge-bases.create")

    sub.add_argument(
        "-d",
        "--description",
        required=False,
        help="KnowledgeBase description"
    )
    sub.add_argument("-f", "--files", nargs="+", required=False, help="The file ids,support multiple values")
    sub.set_defaults(func=KnowledgeBase.create)

    sub = subparsers.add_parser("knowledge-bases.update")

    sub.add_argument("-i", "--id", required=False, help="The knowledgeBase  id")
    sub.add_argument("-d", "--description", required=False, help="KnowledgeBase  description")
    sub.add_argument("-f", "--files", nargs="+", required=False, help="The file ids,support multiple values")
    sub.set_defaults(func=KnowledgeBase.update)

    sub = subparsers.add_parser("knowledge-bases.add_file")
    sub.add_argument("-i", "--id", required=True, help="The knowledge bases ID")
    sub.add_argument(
        "-d",
        "--description",
        required=False,
        help="Description of the file to be added in the knowledge bases"
    )
    sub.add_argument(
        "-f",
        "--file",
        help="Path of the json file to upload"
    )
    sub.set_defaults(func=KnowledgeBase.add_file)

    sub = subparsers.add_parser("knowledge-bases.get")
    sub.add_argument("-i", "--id", required=True, help="The knowledge bases ID")
    sub.set_defaults(func=KnowledgeBase.get)

    sub = subparsers.add_parser("knowledge-bases.delete")
    sub.add_argument("-i", "--id", required=True, help="The knowledge bases ID")
    sub.set_defaults(func=KnowledgeBase.delete)

    sub = subparsers.add_parser("knowledge-bases.list")
    sub.set_defaults(func=KnowledgeBase.list)

    sub = subparsers.add_parser("knowledge-bases.download")
    sub.add_argument("-i", "--id", required=True, help="The knowledge bases ID")
    sub.add_argument("-f", "--file_id", required=True, help="The knowledge bases file ID")
    sub.set_defaults(func=KnowledgeBase.download)

    sub = subparsers.add_parser("knowledge-bases.delete_file")
    sub.add_argument("-i", "--id", required=True, help="The knowledge bases ID")
    sub.add_argument("-f", "--file_id", required=True, help="The knowledge bases file ID")
    sub.set_defaults(func=KnowledgeBase.delete_file)
    # datasets
    sub = subparsers.add_parser("datasets.create")

    sub.add_argument(
        "-d",
        "--description",
        required=False,
        help="Dataset description"
    )
    sub.add_argument("-f", "--files", nargs="+", required=False, help="The file ids,support multiple values")
    sub.set_defaults(func=Dataset.create)

    sub = subparsers.add_parser("datasets.update")

    sub.add_argument("-i", "--id", required=False, help="The datasets  id")
    sub.add_argument("-d", "--description", required=False, help="Dataset  description")
    sub.add_argument("-f", "--files", nargs="+", required=False, help="The file ids,support multiple values")
    sub.set_defaults(func=Dataset.update)

    sub = subparsers.add_parser("datasets.add_file")
    sub.add_argument("-i", "--id", required=True, help="The datasets ID")
    sub.add_argument(
        "-d",
        "--description",
        required=False,
        help="Description of the file to be added in the Dataset"
    )
    sub.add_argument(
        "-f",
        "--file",
        help="Path of the json file to upload"
    )
    sub.set_defaults(func=Dataset.add_file)

    sub = subparsers.add_parser("datasets.get")
    sub.add_argument("-i", "--id", required=True, help="The datasets ID")
    sub.set_defaults(func=Dataset.get)

    sub = subparsers.add_parser("datasets.delete")
    sub.add_argument("-i", "--id", required=True, help="The datasets ID")
    sub.set_defaults(func=Dataset.delete)

    sub = subparsers.add_parser("datasets.list")
    sub.set_defaults(func=Dataset.list)

    sub = subparsers.add_parser("datasets.download")
    sub.add_argument("-i", "--id", required=True, help="The datasets ID")
    sub.add_argument("-f", "--file_id", required=True, help="The datasets file ID")
    sub.set_defaults(func=Dataset.download)

    # models
    sub = subparsers.add_parser("models.get")
    sub.add_argument("-i", "--id", required=True, help="The models ID")
    sub.set_defaults(func=Model.get)

    sub = subparsers.add_parser("models.delete")
    sub.add_argument("-i", "--id", required=True, help="The models ID")
    sub.set_defaults(func=Model.delete)

    sub = subparsers.add_parser("models.list")
    sub.set_defaults(func=Model.list)

    # fine_tunes
    sub = subparsers.add_parser("fine_tunes.list")
    sub.set_defaults(func=FineTune.list)

    sub = subparsers.add_parser("fine_tunes.create")
    sub.add_argument(
        "-t",
        "--training_file",
        required=True,
        help="JSON file containing prompt-completion examples for training. This can "
             "be the ID of a file uploaded through the Sensenova API,"
    )

    sub.add_argument(
        "-m",
        "--model",
        required=True,
        help="The model to start fine-tuning from",
    )
    sub.add_argument(
        "--suffix",
        required=True,
        help="This argument can be used to customize the generated fine-tuned model name."
             "The generated name will match the form `{base_model}-{user}:{suffix}-{timestamp}`. "
    )
    for param in fine_tunes_hyperparams():
        sub.add_argument(
            f"--{param[0]}",
            help=param[1]
        )
    sub.set_defaults(func=FineTune.create)

    sub = subparsers.add_parser("fine_tunes.get")
    sub.add_argument("-i", "--id", required=True, help="The id of the fine-tune")
    sub.set_defaults(func=FineTune.get)

    sub = subparsers.add_parser("fine_tunes.cancel")
    sub.add_argument("-i", "--id", required=True, help="The id of the fine-tune")
    sub.set_defaults(func=FineTune.cancel)

    sub = subparsers.add_parser("fine_tunes.delete")
    sub.add_argument("-i", "--id", required=True, help="The id of the fine-tune")
    sub.set_defaults(func=FineTune.delete)

    # servings
    sub = subparsers.add_parser("servings.list")
    sub.set_defaults(func=Serving.list)

    sub = subparsers.add_parser("servings.create")
    sub.add_argument(
        "-m",
        "--model",
        required=True,
        help="The id of the finetune model"
    )
    sub.add_argument(
        "--run_time",
        required=True,
        type=int,
        help="Specifies the running time, in minutes"
    )
    sub.set_defaults(func=Serving.create)

    sub = subparsers.add_parser("servings.get")
    sub.add_argument("-i", "--id", required=True, help="The id of the serving")
    sub.set_defaults(func=Serving.get)

    sub = subparsers.add_parser("servings.delete")
    sub.add_argument("-i", "--id", required=True, help="The id of the serving")
    sub.set_defaults(func=Serving.delete)

    sub = subparsers.add_parser("servings.cancel")
    sub.add_argument("-i", "--id", required=True, help="The id of the serving")
    sub.set_defaults(func=Serving.cancel)

    sub = subparsers.add_parser("servings.relaunch")
    sub.add_argument("-i", "--id", required=True, help="The id of the serving")
    sub.set_defaults(func=Serving.relaunch)

    # Chat Completions
    sub = subparsers.add_parser("chat_completions.create")

    req = sub.add_argument_group("required arguments")
    opt = sub.add_argument_group("optional arguments")

    req.add_argument(
        "-g",
        "--message",
        action="append",
        nargs=2,
        metavar=("ROLE", "CONTENT"),
        help="A message in `{role} {content}` format. Use this argument multiple times to add multiple messages.",
        required=True,
    )
    req.add_argument(
        "-m",
        "--model",
        help="Model id. Default sensechat-001."
    )
    opt.add_argument(
        "--know_ids",
        nargs='+',
        help="List of knowledge bases id. For example, --know_ids xxx1 xxx2 xxx3."
    )
    opt.add_argument(
        "--temperature",
        type=float,
        help="Temperature sampling parameter,"
             "the value is (0,2]."
             "Values greater than 1 tend to generate more diverse replies, and values less than 1 tend to generate more "
             "stable replies. "
             "Default 0.8"
    )
    opt.add_argument(
        "--top_p",
        type=float,
        help="Kernel sampling parameter, the value is (0,1]."
             " When decoding and generating tokens, sampling is performed in the minimum token set whose probability"
             " sum is greater than or equal to top_p. "
             "Default 0.7"
    )
    opt.add_argument(
        "--max_new_tokens",
        type=int,
        help="The maximum number of tokens generated."
             " Default 2048."
    )
    opt.add_argument(
        "--repetition_penalty",
        type=float,
        help="Repeat penalty factor, 1 means no penalty, "
             "greater than 1 tends to generate non-repeat token, "
             "less than 1 tends to generate repeat token."
             " Default 1"
    )
    opt.add_argument(
        "--stream", help="Stream messages as they're ready.", action="store_true"
    )
    opt.add_argument(
        "--user",
        help="User id."
    )
    sub.set_defaults(func=ChatCompletion.create)

    # finetune_completion
    # sub = subparsers.add_parser("finetune_completions.create")
    #
    # req = sub.add_argument_group("required arguments")
    # opt = sub.add_argument_group("optional arguments")
    #
    # req.add_argument(
    #     "-m",
    #     "--model_id",
    #     required=True,
    #     help="Model id."
    # )
    #
    # req.add_argument(
    #     "-t",
    #     "--text",
    #     required=True,
    #     help="Input messages."
    # )
    #
    # opt.add_argument(
    #     "--stream", help="Stream messages as they're ready.", action="store_true"
    # )
    #
    # for param in finetune_completions_option_params():
    #     opt.add_argument(f"--{param[0]}", help=param[1])
    #
    # sub.set_defaults(func=FinetuneCompletion.create)

    # File API
    sub = subparsers.add_parser("files.create")
    req = sub.add_argument_group("required arguments")
    opt = sub.add_argument_group("optional arguments")
    req.add_argument("-f", "--file", help="Path of the json file to upload", required=True)
    req.add_argument("-s", "--scheme", help="The file type.", required=True)
    opt.add_argument("-d", "--description", help="The file description.",required=False)
    sub.set_defaults(func=File.create)

    sub = subparsers.add_parser("files.list")
    sub.set_defaults(func=File.list)

    sub = subparsers.add_parser("files.get")
    sub.add_argument("-i", "--id", required=True, help="The id of the file")
    sub.set_defaults(func=File.get)

    sub = subparsers.add_parser("files.download")
    sub.add_argument("-i", "--id", required=True, help="The id of the file")
    sub.set_defaults(func=File.download)

    sub = subparsers.add_parser("files.delete")
    sub.add_argument("-i", "--id", required=True, help="The id of the file")
    sub.set_defaults(func=File.delete)

    # ChatSession
    sub = subparsers.add_parser("chat_sessions.create")

    sub.add_argument(
        "-p",
        "--prompts",
        action="append",
        nargs=2,
        metavar=("ROLE", "CONTENT"),
        help="A prompt in `{role} {content}` format. Use this argument multiple times to add multiple messages.",
        required=False,
    )
    sub.set_defaults(func=ChatSession.create)

    # Chat Conversation
    sub = subparsers.add_parser("chat_conversations.create")

    req = sub.add_argument_group("required arguments")
    opt = sub.add_argument_group("optional arguments")

    req.add_argument("-m", "--model", help="Model id. Default empty.", required=True)
    req.add_argument("-c", "--content", help="The chat content.", required=True)
    req.add_argument("-s", "--session_id", help="The session id.", required=True)
    opt.add_argument(
        "-a", "--action",
        help="continue the conversation use `next`,"
             "regeneration within an existing round of conversation use `regeneration`,"
             "default is `next`",
    )
    opt.add_argument(
        "--know_ids",
        nargs='+',
        help="List of knowledge bases id. For example, --know_ids xxx1 xxx2 xxx3."
    )
    opt.add_argument("-t", "--stream", help="Stream messages as they're ready.", action="store_true")

    sub.set_defaults(func=ChatConversation.create)

class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def display_error(e):
    extra = (
        " (HTTP status code: {})".format(e.http_status)
        if e.http_status is not None
        else ""
    )
    sys.stderr.write(
        "{}Error:{} {}{}\n".format(
            bcolors.FAIL, bcolors.ENDC, e, extra
        )
    )
