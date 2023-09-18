"""
`proword` python package allowing you to develop terminal applications with minimal 
dependencies for greater developer experience. 📦🚀
"""
import json
from attrs import define


@define
class LocalData:
    """
    `LocalData` is a solution to saving values and more onto a local user's hard drive using JSON module and allows for developers to 
    easily access saved values and store.

    Visit https://proword.vercel.app/API/Data for more information.
    
    Arguments:
        filename: str = "local.json" - Used to designate where values is stored
    """

    filename: str = "local.json"
    data = {}

    def serialize(self, key: str, value: any):
        """
        Adds a identifiable key to a value given by the developer during runtime.

        Args:
            key (str): Identifiable and unique key for storage
            value (any): Value(s) to be serialized with JSON
        """
        self.data[key] = value

    def save(self):
        """
        Saves serialized values to a local JSON file.
        """
        with open(self.filename, "w") as file:
            json.dump(self.data, file, indent=4)

    @staticmethod
    def load(filename: str):
        """
        Load a local JSON file and puts the values into a dict for easy picking.

        Args:
            filename (str): JSON file

        Returns:
            dict: JSON data
        """
        with open(filename, "r") as file:
            data = json.load(file)
        return data
