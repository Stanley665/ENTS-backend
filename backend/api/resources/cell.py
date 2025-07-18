from flask_restful import Resource
from flask import request, jsonify
from ..auth.auth import authenticate
from ..schemas.cell_schema import CellSchema

# from ..conn import engine
from ..models.cell import Cell as CellModel
from ..schemas.add_cell_schema import AddCellSchema

cells_schema = CellSchema(many=True)
add_cell_schema = AddCellSchema()

# pt 2: use flask restful to add a decorator for the get endpoint


class Cell(Resource):
    method_decorators = {"get": [authenticate]}

    def get(self, user):
        json_data = request.args
        userCells = json_data.get("user")

        if userCells:
            cells = CellModel.get_cells_by_user_id(user.id)
            return cells_schema.dump(cells)
        else:
            cells = CellModel.get_all()
            return cells_schema.dump(cells)

    def post(self):
        json_data = request.json
        cell_data = add_cell_schema.load(json_data)
        cell_name = cell_data["name"]
        location = cell_data["location"]
        lat = cell_data["latitude"]
        long = cell_data["longitude"]
        userEmail = cell_data["userEmail"]
        # FIXME:
        # migrate user email to include authenticated user
        # if userEmail["userEmail"] is None:
        #     userEmail = cell_data["userEmail"]
        if cell_data["archive"] is None:
            archive = False
        else:
            archive = cell_data["archive"]
        if CellModel.find_by_name(cell_name):
            return {"message": "Duplicate cell name"}, 400
        new_cell = CellModel.add_cell_by_user_email(
            cell_name, location, lat, long, archive, userEmail
        )
        if new_cell:
            return {"message": "Successfully added cell"}
        return {"message": "Error adding cell"}, 400

    def put(self, cellId):
        json_data = request.json
        # print("Received payload:", json_data)
        # archive = json_data.get("archive")
        cell = CellModel.get(cellId)

        if cell:
            if "name" in json_data:
                cell.name = json_data.get("name")
            if "location" in json_data:
                cell.location = json_data.get("location")
            if "lat" in json_data:
                cell.latitude = json_data.get("lat")
            if "long" in json_data:
                cell.longitude = json_data.get("long")
            if "archive" in json_data:
                cell.archive = json_data.get("archive")

            cell.save()
            return {"message": "Successfully updated cell"}
        return jsonify({"message": "Cell not found"}), 404

    def delete(self, cellId):
        cell = CellModel.get(cellId)
        if not cell:
            return jsonify({"message": "Cell not found"}), 404
        cell.delete()

        return {"message": "Cell deleted successfully"}
