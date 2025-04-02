# Sample syllabus mapping for Indian curriculum
SYLLABUS = {
    "mathematics": {
        "5": ["Numbers", "Operations", "Fractions", "Geometry", "Measurement"],
        "6": ["Integers", "Algebra", "Ratio and Proportion", "Basic Geometry"],
        "7": ["Number System", "Algebra", "Data Handling", "Mensuration"]
    },
    "science": {
        "5": ["Plants", "Animals", "Natural Resources", "Environment"],
        "6": ["Food", "Materials", "Living Organisms", "Motion"],
        "7": ["Nutrition", "Fibre to Fabric", "Heat", "Acids and Bases"]
    }
}

class SyllabusMapper:
    def get_related_topics(self, subject: str, grade: str) -> list[str]:
        return SYLLABUS.get(subject.lower(), {}).get(grade, [])