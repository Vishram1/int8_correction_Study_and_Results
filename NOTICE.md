# Terms and external materials

No repository-wide software or manuscript reuse license has been selected. This packaging step does not assign an MIT, Apache, Creative Commons, or other license on the author's behalf. Add the intended license when the author chooses one; citation metadata alone is not a license grant.

The manuscript names Vishwaram Reddy. The project source, correction parameters and derived statistical evidence are included for this research record. Existing notices in source files remain intact.

External dependencies retain their own terms:

- Qualcomm AI Runtime / QNN SDK and runtime libraries are not redistributed. Obtain QAIRT 2.45.41.260507 from its provider under the applicable terms.
- Pretrained model archives originate from Qualcomm AI Hub model release v0.63.0 and their upstream model authors. Download URLs and exact recorded hashes are in `environment/external-assets.json`; no weight redistribution license is inferred from a public download URL.
- ImageNetV2 image pixels are not included. The repository includes image identities, class labels and hashes needed to describe the evaluation split. Images retain their source usage terms; a repository's code license does not necessarily license its images.
- NumPy, Matplotlib, AIMET, ONNX, PyTorch, Android NDK and other dependencies are obtained separately under their respective licenses. Their source/binaries are not vendored here.

The public audit is an explicitly labeled derivative. Private original phone returns retain their original serials and hashes outside this repository. Anonymization has not changed predictions, numerical results or the recorded identity/build linkage between validation and final acquisition.
