
import copy
import logging

logger = logging.getLogger(__name__)

class HardwareSet(object):
    """A class to manage the categorized instance types.
    
    It takes flat instance types array and builds a nested structure where instance types exist in
    categories.
    
    If after categorization there is only one category and it is the misc category, then we
    recategorize by cpu and gpu.
    """

    def __init__(self, instance_types):

        self.instance_types = self.build_unique(instance_types)
        self.categories = self.build_categories()

    @staticmethod
    def build_unique(instance_types):
        """Build a dictionary of instance types using name as key.
        
        Remove any instance types whose description has already been seen. We can't have duplicate
        descriptions.
        
        If categories exist, then remove any instance types that don't have a category. Otherwise,
        since there are no categories, we can't remove any instance types.
        """
        categories = [category for it in instance_types for category in (it.get("categories") or [])]
        result = {}
        seen_descriptions = set() 
        for it in instance_types:
            if it["description"] in seen_descriptions:
                continue
            if categories:
                if it.get("categories") in [[], None]:
                    continue
            else:
                # make our own categories GPU/CPU
                it["categories"] = [{'label': 'GPU', 'order': 2}] if "gpu" in it and it["gpu"] else [{'label': 'CPU', 'order': 1}]
            result[it["name"]] = it
            seen_descriptions.add(it["description"])
        return result
    
    
    def build_categories(self):
        """Build a sorted list of categories, each category containing a sorted list of machines"""
 
        dikt = {}
        for key in self.instance_types:
            it = self.instance_types[key]
            categories = it["categories"]
            for category in categories:
                label = category["label"]
                if label not in dikt:
                    dikt[label] = {"label": label, "content": [], "order": category["order"]}
                dikt[label]["content"].append(it)

        result = []
        for label in dikt:
            category = dikt[label]
            category["content"].sort(key=lambda k: (k["cores"], k["memory"]))
            result.append(category)
        return sorted(result, key=lambda k: k["order"])
 
    def recategorize(self, partitioner):
        """Recategorize the instance types.

        Partitioner is a function that takes an instance type and returns a list of categories.
        
        If for example you want to append to the existing categories, then you can use a function like this:
        lambda x: x["categories"] + [{'label': 'Low cores', 'order': 10}] if  x["cores"] < 16 else [{'label': 'High cores', 'order': 20}]
        
        Rebuilds the categories structure after assigning the new categories.
        """
        for key in self.instance_types:
            self.instance_types[key]["categories"] = partitioner(self.instance_types[key])
        self.categories = self.build_categories()


    def get_model(self, with_misc=False):
        """Returns the categories structure with renaming ready for some UI.

        NOTE: THIS METHOD WILL BE DEPRECATED. with_misc is no longer used, which means that this
        function just renames a few keys. What's more, the init function ensures that every instance
        type has a (non-misc) category. So this function is no longer needed. Submitters that use
        it will work fine, but should be updated to use the categories structure directly. 
        """
        if with_misc:
            logger.warning("with_misc is no longer used")
        result = []
        for category in self.categories:
            result.append({
                "label": category["label"],
                "content": [{"label": k["description"], "value": k["name"]} for k in category["content"]]
            })

        return result
    
    def find(self, name):
        """Find an instance type by name (sku).
        
        Example: find("p3.2xlarge")
        
        Returns and instance-type or None if not found.
        """
        return self.instance_types.get(name)
    
    def find_category(self, label):
        """Find a category by label.
        
        Example: find_category("GPU")
        
        Returns the entire category and its contents or None if not found. 
        """
        return next((c for c in self.categories if c["label"] == label), None)
    
    
    def find_all(self, condition):
        """Find all instance types that match a condition.
        
        Example: find_all(lambda x: x["gpu"])
        """
        result = []
        for key in self.instance_types:
            if condition(self.instance_types[key]):
                result.append(self.instance_types[key])
        return result
    
    def find_first(self, condition):
        """Find the first instance type that matches a condition.
        
        Example: find_first(lambda x: x["cores"] == 4)"])
        """
        return next(iter(self.find_all(condition)), None)
    
    def number_of_categories(self):
        """Return the number of categories in the data."""
        return len(self.categories)
    