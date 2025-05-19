from collections import OrderedDict
from pathlib import Path
from typing import List


class CY_TextBox():
    CATEGORY = "CY"
    FUNCTION = "show_text"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "","multiline": True}),
            }
        }
    
    def show_text(self, text):
        return (text,)

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)


class CY_LoadPrompt():
    CATEGORY = "CY"
    FUNCTION = "load_prompt"

    prompt_folder = Path(__file__).parent / "prompts"

    @classmethod
    def INPUT_TYPES(cls):
        prompt_files = glob_files(cls.prompt_folder, ".txt")
        return {
            "required": {
                "prompt_file": (sorted(prompt_files),),
            }
        }

    def load_prompt(
        self,
        prompt_file: str,
    ):
        loaded_tags = load_prompt_file(self.prompt_folder / f"{prompt_file}.txt")
        prompt = ", ".join(loaded_tags)
        return (prompt,)

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)


class CY_LoadPrompt4():
    CATEGORY = "CY"
    FUNCTION = "load_prompt_multi"

    empty_prompt = "-----"
    prompt_folder = Path(__file__).parent / "prompts"

    @classmethod
    def INPUT_TYPES(cls):
        prompt_files = [cls.empty_prompt] + list(glob_files(cls.prompt_folder, ".txt"))
        return {
            "required": {
                "remove_duplicate": ("BOOLEAN", {"default": True}),
                "prompt": ("STRING", {"default": ""}),
                "file1": (prompt_files, {"default": cls.empty_prompt}),
                "file2": (prompt_files, {"default": cls.empty_prompt}),
                "file3": (prompt_files, {"default": cls.empty_prompt}),
                "file4": (prompt_files, {"default": cls.empty_prompt}),
            }
        }

    def load_prompt_multi(
        self,
        remove_duplicate: bool,
        prompt: str,
        file1: str,
        file2: str,
        file3: str,
        file4: str,
    ):
        edited_tags = OrderedDict()
        if len(prompt) > 0:
            update_tag_dict(edited_tags, process_tag_str(prompt), remove_duplicate)

        for file_path in [file1, file2, file3, file4]:
            if file_path != self.empty_prompt:
                loaded_tags = load_prompt_file(self.prompt_folder / f"{file_path}.txt")
                update_tag_dict(edited_tags, loaded_tags, remove_duplicate)

        prompt = "".join([f"{t}, " * n for t, n in edited_tags.items()])
        return (prompt,)

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)


class CY_LoadPromptPro():
    CATEGORY = "CY"
    FUNCTION = "load_prompt_pro"

    empty_prompt = "-----"
    prompt_folder = Path(__file__).parent / "prompts"
    character_folder = Path(__file__).parent / "prompts"/ "character"
    cloth_folder = Path(__file__).parent / "prompts"/ "cloth"
    pose_folder = Path(__file__).parent / "prompts"/ "pose"
    style_folder = Path(__file__).parent / "prompts"/ "style"

    @classmethod
    def INPUT_TYPES(cls):
        charcater_prompt_files = [f.stem for f in cls.character_folder.iterdir() if f.suffix == ".txt"]
        cloth_prompt_files = [cls.empty_prompt] + [f.stem for f in cls.cloth_folder.iterdir() if f.suffix == ".txt"]
        pose_prompt_files = [cls.empty_prompt] + [f.stem for f in cls.pose_folder.iterdir() if f.suffix == ".txt"]
        style_prompt_files = [cls.empty_prompt] + [f.stem for f in cls.style_folder.iterdir() if f.suffix == ".txt"]
        return {
            "required": {
                "remove_duplicate": ("BOOLEAN", {"default": True}),
                "character": (sorted(charcater_prompt_files),),
                "cloth": (sorted(cloth_prompt_files), {"default": cls.empty_prompt}),
                "pose": (sorted(pose_prompt_files), {"default": cls.empty_prompt}),
                "style": (sorted(style_prompt_files), {"default": cls.empty_prompt}),
            }
        }

    def load_prompt_pro(
        self,
        remove_duplicate: bool,
        character: str,
        cloth: str,
        pose: str,
        style: str
    ):
        edited_tags = OrderedDict()

        character_tags = load_prompt_file(self.character_folder / f"{character}.txt")
        edited_tags = update_tag_dict(edited_tags, character_tags, remove_duplicate)
        if cloth != self.empty_prompt:
            cloth_tags = load_prompt_file(self.cloth_folder / f"{cloth}.txt")
            edited_tags = update_tag_dict(edited_tags, cloth_tags, remove_duplicate)
        if pose != self.empty_prompt:
            pose_tags = load_prompt_file(self.pose_folder / f"{pose}.txt")
            edited_tags = update_tag_dict(edited_tags, pose_tags, remove_duplicate)
        if style != self.empty_prompt:
            style_tags = load_prompt_file(self.style_folder / f"{style}.txt")
            edited_tags = update_tag_dict(edited_tags, style_tags, remove_duplicate)

        prompt = "".join([f"{t}, " * n for t, n in edited_tags.items()])
        return (prompt,) 

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)


class CY_PromptComposer():
    CATEGORY = "CY"
    FUNCTION = "compose_prompt"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": ""}),
                "add_tag": ("STRING", {"default": "","multiline": True}),
                "remove_tag": ("STRING", {"default": "","multiline": True}),
                "remove_duplicate": ("BOOLEAN", {"default": True}),
            },
        }

    def compose_prompt(
        self,
        prompt: str,
        add_tag: str,
        remove_tag: str,
        remove_duplicate: bool,
    ):
        edited_tags = OrderedDict()

        if len(prompt) != 0:
            loaded_tags = process_tag_str(prompt)
            edited_tags = update_tag_dict(edited_tags, loaded_tags, remove_duplicate)

        if len(add_tag) > 0:
            add_tag = process_tag_str(add_tag)
            edited_tags = update_tag_dict(edited_tags, add_tag, remove_duplicate)

        if len(remove_tag) > 0:
            remove_tags = process_tag_str(remove_tag)
            for tag in remove_tags:
                if tag in edited_tags:
                    del edited_tags[tag]

        prompt = "".join([f"{t}, " * n for t, n in edited_tags.items()])
        return (prompt,)

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    OUTPUT_NODE = True


def process_tag_str(tag_str: str) -> List[str]:
    tags = []
    for tag in tag_str.split(","):
        tag = tag.strip()
        if tag == "":
            continue
        tags.append(tag)
    return tags

def load_prompt_file(file_path: str) -> List[str]:
    with Path(file_path).open("r", encoding="utf-8") as f:
        prompt = f.read()
    return process_tag_str(prompt)

def update_tag_dict(tag_dict: OrderedDict, new_tags: List[str], remove_duplicate: bool = True) -> OrderedDict:
    for tag in new_tags:
        if remove_duplicate or tag not in tag_dict:
            tag_dict[tag] = 1
        else:
            tag_dict[tag] += 1
    return tag_dict

def glob_files(base_folder: str, suffix: str) -> List[str]:
    files = []
    for file in Path(base_folder).rglob(f"*{suffix}"):
        file = str(file.relative_to(base_folder).with_suffix(""))
        files.append(file)
    return sorted(files)


NODE_CLASS_MAPPINGS = {
    "CY_TextBox": CY_TextBox,
    "CY_LoadPrompt": CY_LoadPrompt,
    "CY_LoadPrompt4": CY_LoadPrompt4,
    "CY_LoadPromptPro": CY_LoadPromptPro,
    "CY_PromptComposer": CY_PromptComposer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CY_TextBox": "CY_TextBox",
    "CY_LoadPrompt": "CY_LoadPrompt",
    "CY_LoadPrompt4": "CY_LoadPrompt4",
    "CY_LoadPromptPro": "CY_LoadPromptPro",
    "CY_PromptComposer": "CY_PromptComposer",
}
