#!/usr/bin/python3
# -*- coding: utf-8 -*-

from kot import KOT, KOT_Remote, HASHES, console

class KOT_Update:
    def __init__(self, cloud) -> None:
        self.cloud = cloud
        self.pre_update_dict = {}
    def pre_update(self, key):
        self.pre_update_dict[key] = self.cloud.get(key, encryption_key=None)
    def update(self):
        console.log("[bold green] Update Started")
        the_update_list = str(list(self.pre_update_dict))
        console.log(f"[bold white] Updating: {the_update_list}")
        error = False
        for key in self.pre_update_dict:
            result = False
            currently = self.pre_update_dict[key]
            new = new = self.cloud.get(key, encryption_key=None)


            if currently != new:
                result = True
            
            
            if result:
                console.log(f" {key}: [bold green]OK")
            else:
                error = True
                console.log(f" {key}: [bold red]Failure")

        if error:
            console.log("[bold red] Updating Complated With Error")
        else:
            console.log("[bold green] Updating Complated Without any Error")
