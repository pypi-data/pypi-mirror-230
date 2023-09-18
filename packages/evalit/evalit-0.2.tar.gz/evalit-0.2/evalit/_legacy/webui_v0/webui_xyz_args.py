class WebuiXyzArgs:
    AXIS_TYPE_MAP = {
        "Nothing": 0,
        "Seed": 1,
        "Var. seed": 2,
        "Var. strength": 3,
        "Steps": 4,
        "Hires steps": 5,
        "CFG Scale": 6,
        "Prompt S/R": 7,
        "Prompt order": 8,
        "Sampler": 9,
        "Checkpoint name": 10,
        "Negative Guidance minimum sigma": 11,
        "Sigma Churn": 12,
        "Sigma min": 13,
        "Sigma max": 14,
        "Sigma noise": 15,
        "Schedule type": 16,
        "Schedule min sigma": 17,
        "Schedule max sigma": 18,
        "Schedule rho": 19,
        "Eta": 20,
        "Clip skip": 21,
        "Denoising": 22,
        "Hires upscaler": 23,
        "VAE": 24,
        "Styles": 25,
        "UniPC Order": 26,
        "Face restore": 27,
        "Token merging ratio": 28,
        "Token merging ratio high-res": 29,
    }

    def __init__(
        self, x_axis: list = None, y_axis: list = None, z_axis: list = None
    ) -> None:
        """
        common axis_type:
        - "Nothing"(not using the axis)
        - "Seed", "Steps", "CFG Scale", "Sampler", "Checkpoint name", "VAE"

        for complete list: see AXIS_TYPE_MAP defined in the class

        also check the `axis_options` definition in webui_v0 for updates:
            https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/master/scripts/xyz_grid.py

        :param x_axis: [axis_type, values, values_dropdown] or [axis_type, values]; eg. ["Seed", "12345, 54321"]
        :param y_axis:
        :param z_axis:
        """
        self.x_type, self.x_values, self.x_values_dropdown = self._unpack_axis(x_axis)
        self.y_type, self.y_values, self.y_values_dropdown = self._unpack_axis(y_axis)
        self.z_type, self.z_values, self.z_values_dropdown = self._unpack_axis(z_axis)
        self.draw_legend = True
        self.include_lone_images = False
        self.include_sub_grids = False
        self.no_fixed_seeds = False
        self.margin_size = 1

    def _unpack_axis(self, axis: list) -> tuple[str, str, str]:
        """unpacks input axis value list into 3 parts: axis_type, values, values_dropdown"""
        if axis is None:
            return "Nothing", "", ""
        if len(axis) == 2:
            return axis[0], axis[1], ""
        elif len(axis) == 3:
            return tuple(axis)
        else:
            raise ValueError("Invalid axis format")

    def __iter__(self):
        return iter(self.to_list())

    def __repr__(self):
        return (
            f"XyzScriptArg(x_type={self.x_type}, x_values={self.x_values}, x_values_dropdown={self.x_values_dropdown}, "
            f"y_type={self.y_type}, y_values={self.y_values}, y_values_dropdown={self.y_values_dropdown}, "
            f"z_type={self.z_type}, z_values={self.z_values}, z_values_dropdown={self.z_values_dropdown}, "
            f"draw_legend={self.draw_legend}, include_lone_images={self.include_lone_images}, "
            f"include_sub_grids={self.include_sub_grids}, no_fixed_seeds={self.no_fixed_seeds}, margin_size={self.margin_size})"
        )

    def to_list(self) -> list:
        """输出设置为webui api需要的格式, 也可以直接List(WebuiXyzArgs)得到"""
        return [
            self.AXIS_TYPE_MAP.get(self.x_type, 0),
            self.x_values,
            self.x_values_dropdown,
            self.AXIS_TYPE_MAP.get(self.y_type, 0),
            self.y_values,
            self.y_values_dropdown,
            self.AXIS_TYPE_MAP.get(self.z_type, 0),
            self.z_values,
            self.z_values_dropdown,
            self.draw_legend,
            self.include_lone_images,
            self.include_sub_grids,
            self.no_fixed_seeds,
            self.margin_size,
        ]

    def set_x_axis(self, axis_type, values, values_dropdown=""):
        self.x_type = axis_type
        self.x_values = values
        self.x_values_dropdown = values_dropdown

    def set_y_axis(self, axis_type, values, values_dropdown=""):
        self.y_type = axis_type
        self.y_values = values
        self.y_values_dropdown = values_dropdown

    def set_z_axis(self, axis_type, values, values_dropdown=""):
        self.z_type = axis_type
        self.z_values = values
        self.z_values_dropdown = values_dropdown

    def set_plot_options(
        self,
        draw_legend=True,
        include_lone_images=False,
        include_sub_grids=False,
        no_fixed_seeds=False,
        margin_size=1,
    ):
        self.draw_legend = draw_legend
        self.include_lone_images = include_lone_images
        self.include_sub_grids = include_sub_grids
        self.no_fixed_seeds = no_fixed_seeds
        self.margin_size = margin_size


if __name__ == "__main__":
    # Example usage
    xyz_script_args = WebuiXyzArgs(
        x_axis=["Steps", "20,30"],
        y_axis=["Sampler", "Euler a, LMS"],
        z_axis=["Nothing", ""],
    )
    new_args = list(xyz_script_args)
    print(new_args)
