# Package Reader

The package reader allows you to read installed services and their configuration. For this the service `service-misc`
has to be running on the system.

## Testing

For testing a mock version of the package reader is available. Example:

```python
from openmodule_test.package_reader import MockPackageReader

package_reader = MockPackageReader()
package_reader.services.add_hardware_package("hw_compute_nuc_1", hardware_type=["compute"], ip="10.15.0.200")
package_reader.services.add_software_package("om_fancy_assistant_1", parent="hw_compute_nuc_1",
                                             env={"LOG_LEVEL": " DEBUG"})

print(package_reader.get_service_by_name("om_fancy_assistant_1").parent.name)
# hw_compute_nuc_1
```
