In Clean Architecture, **domain entities** are not supposed to directly use repositories. Here's why and how this principle is applied:

### Why Domain Entities Should Not Use Repositories
1. **Separation of Concerns**: 
   - Domain entities represent the core business objects and encapsulate their intrinsic business rules and data (e.g., validation logic, state changes). They should focus solely on the business logic inherent to the entity itself, such as ensuring an invoice has a valid amount or vendor.
   - Repositories, on the other hand, belong to the **Interface Adapters** or **Infrastructure Layer** (or are defined as interfaces in the **Domain Layer** but implemented in the Infrastructure Layer). They handle data persistence and retrieval, which is an infrastructure concern, not a core business rule.

2. **Dependency Rule**: 
   - Clean Architecture enforces the **Dependency Rule**, which states that dependencies should point inward toward the Domain Layer. Entities are at the core of the architecture and should not depend on outer layers, such as repositories, which rely on external systems (e.g., databases, file systems).
   - Allowing entities to use repositories would create a dependency from the Domain Layer to the Infrastructure Layer, violating this rule and making the entities less portable and harder to test.

3. **Testability**: 
   - Entities should be pure and self-contained, making them easy to test without mocking external dependencies like databases. If an entity uses a repository, unit tests would require mocking the repository, increasing complexity and coupling.

4. **Single Responsibility**: 
   - Entities are responsible for maintaining their own state and enforcing business rules. Repositories are responsible for data access. Mixing these concerns in an entity would violate the Single Responsibility Principle.

### Where Does Data-Dependent Logic Go?
If business logic requires data access (e.g., looking up vendor terms or holiday dates to calculate an invoice due date, as in your previous example), this logic should be placed in a **Domain Service** or handled within a **Use Case**, not the entity itself. Here's how:

- **Domain Service**: A stateless component in the Domain Layer that orchestrates complex business logic involving multiple entities or external data. It can depend on repository interfaces (defined in the Domain Layer) to fetch data without coupling to the Infrastructure Layer.
- **Use Case**: Orchestrates the application-specific flow, interacting with entities, domain services, and repository interfaces to perform tasks like creating an invoice or calculating a due date.

For example, in the invoice entry use case:
- The `InvoiceEntity` handles intrinsic validations (e.g., ensuring the amount is positive).
- A `InvoiceValidationService` (Domain Service) calculates the due date by fetching vendor terms and holiday dates via `VendorRepository` and `HolidayRepository` interfaces.
- The `ManualInvoiceUseCase`, `OCRInvoiceUseCase`, or `FreightIntegrationInvoiceUseCase` coordinates the process, calling the entity and domain service as needed.

### Example Clarification
In the previous code example, the `InvoiceEntity` did not directly use repositories. Instead:
- The `InvoiceValidationService` (a Domain Service) depended on `VendorRepository` and `HolidayRepository` interfaces to fetch data.
- The use cases (`ManualInvoiceUseCase`, etc.) injected the `InvoiceValidationService` and coordinated the creation of `InvoiceEntity` instances, ensuring the entity remained pure.

Here’s a simplified snippet to illustrate the separation:

```typescript
// Domain Layer: Entity
class InvoiceEntity {
  private constructor(public invoice: Invoice) {}

  static create(data: { vendorId: string; amount: number; dueDate: Date }): InvoiceEntity {
    // Intrinsic validation (no repository dependency)
    if (!data.vendorId) throw new Error('Vendor ID is required');
    if (data.amount <= 0) throw new Error('Amount must be positive');
    return new InvoiceEntity({ ...data, id: Math.random().toString(36).substring(2, 15), status: 'pending' });
  }
}

// Domain Layer: Domain Service
class InvoiceValidationService {
  constructor(
    private vendorRepository: VendorRepository,
    private holidayRepository: HolidayRepository
  ) {}

  async calculateDueDate(vendorId: string, baseDate: Date): Promise<Date> {
    const vendor = await this.vendorRepository.findById(vendorId);
    if (!vendor) throw new Error('Vendor not found');
    const dueDate = new Date(baseDate);
    dueDate.setDate(baseDate.getDate() + vendor.paymentTermsDays);
    // Adjust for holidays using holidayRepository...
    return dueDate;
  }
}

// Use Case Layer
class ManualInvoiceUseCase {
  constructor(
    private invoiceRepository: InvoiceRepository,
    private validationService: InvoiceValidationService
  ) {}

  async execute(input: InvoiceInput): Promise<InvoiceOutput> {
    const dueDate = await this.validationService.calculateDueDate(input.vendorId, new Date(input.invoiceDate));
    const invoiceEntity = InvoiceEntity.create({ vendorId: input.vendorId, amount: input.amount, dueDate });
    await this.invoiceRepository.save(invoiceEntity.invoice);
    return { id: invoiceEntity.invoice.id, /* ...other fields */ };
  }
}
```

### Key Points
- **Entity (`InvoiceEntity`)**: Contains only intrinsic business rules (e.g., validating vendor ID and amount). It has no knowledge of repositories or external data.
- **Domain Service (`InvoiceValidationService`)**: Handles data-dependent logic (e.g., due date calculation) by using repository interfaces, keeping the logic in the Domain Layer.
- **Use Case**: Coordinates the flow, using the entity and domain service, and interacts with repositories for persistence.
- **Dependency Injection**: Repositories are injected into the Domain Service or Use Case, ensuring the entity remains decoupled.

### Exceptions and Edge Cases
In rare cases, you might see patterns where entities appear to interact with repositories, but this is typically a design smell. For example:
- If an entity needs to validate its state against external data (e.g., checking if a vendor exists), this should be handled by a Domain Service or Use Case before creating the entity.
- If an entity needs to perform complex operations involving other entities, a Domain Service can encapsulate this logic, keeping the entity focused on its own state.

### Practical Implications
- **Testability**: The `InvoiceEntity` can be tested in isolation without mocking repositories. The `InvoiceValidationService` can be tested by mocking the `VendorRepository` and `HolidayRepository` interfaces.
- **Flexibility**: The Domain Layer remains independent of the database or framework, allowing you to swap out infrastructure (e.g., from in-memory to MongoDB) without changing the entity or domain service.
- **Maintainability**: By keeping entities pure, you avoid scattering data access logic across the domain, making the codebase easier to maintain.

If you want to explore a specific scenario (e.g., additional validation requiring data access, testing strategies, or integrating with a real database), let me know, and I can provide a tailored example or explanation!