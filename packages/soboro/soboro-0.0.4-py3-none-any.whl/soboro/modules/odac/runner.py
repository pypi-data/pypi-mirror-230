# pyright: reportShadowedImports=false
from typing import *

from ...common import Detection, Image, Images
from ...runner import Runner, RunnerConfig

__all__ = ["ODACRunnerConfig", "ODACRunner"]


class ODACRunnerConfig(RunnerConfig, dynamic=True):
    type: str = "ODACRunner"
    detector: RunnerConfig
    tracker: RunnerConfig = None


class ODACRunner(Runner):
    config_type: Type[RunnerConfig] = ODACRunnerConfig
    outputs: List[str] = ["detections"]

    def prepare(self) -> "Runner":
        config: ODACRunnerConfig = self.config

        self.detector = Runner.create(config.detector)
        self.detector.prepare()

        self.tracker = None
        if config.tracker is not None:
            self.tracker = Runner.create(config.tracker)
            self.tracker.prepare()

    def run(
        self, images: Union[Image, Images], **kwargs
    ) -> Union[List[Detection], List[List[Detection]]]:
        is_single_image = type(images) is not list
        if is_single_image:
            images = [images]

        images_detection = self.detector.run(images)
        results = []
        for detections in images_detection:
            if self.tracker:
                tracks = self.tracker.run(detections=detections)
                results.append([track.detection for track in tracks])
                continue

            results.append(detections)

        if is_single_image:
            return results[0]

        return results
