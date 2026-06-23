# 📊 Diagrama de Arquitetura — Migração PowerCenter → Fabric via MCP

## Fluxo de Migração End-to-End

```mermaid
graph TB
    subgraph Local["💻 Ambiente Local"]
        A[Repositório Git] --> B[Scripts Python]
        B --> C[Notebooks PySpark]
        B --> D[XMLs Source]
        B --> E[Pipeline Configs]
    end
    
    subgraph MCP["🔌 Microsoft Fabric MCP"]
        F[fabric_mcp_migration.py]
        F --> G[FabricMCPClient]
        G --> H[Azure AD Auth]
    end
    
    subgraph Fabric["☁️ Microsoft Fabric"]
        I[Workspace]
        J[Lakehouse]
        K[Notebooks]
        L[Data Pipelines]
        M[Delta Tables]
    end
    
    A --> F
    C --> F
    D --> F
    E --> F
    
    H --> I
    I --> J
    I --> K
    I --> L
    J --> M
    
    style F fill:#00BCF2
    style I fill:#FFB900
    style J fill:#00A4EF
    style M fill:#10893E
```

---

## Arquitetura de Componentes

```mermaid
graph LR
    subgraph PowerCenter["🔵 PowerCenter (Legacy)"]
        P1[wf_m_poc_xml_emp]
        P2[wf_m_poc_xml_hr]
        P3[XML Mappings]
    end
    
    subgraph Tradução["🔄 Camada de Tradução"]
        T1[PowerCenter Parser]
        T2[Mapping Analyzer]
        T3[PySpark Generator]
    end
    
    subgraph Fabric["🟢 Microsoft Fabric"]
        F1[Notebook 03: Map EMP]
        F2[Notebook 05: Map HR]
        F3[Pipeline EMP]
        F4[Pipeline HR]
        F5[Delta Tables]
    end
    
    P1 --> T1
    P2 --> T1
    P3 --> T2
    
    T1 --> T3
    T2 --> T3
    
    T3 --> F1
    T3 --> F2
    
    F1 --> F3
    F2 --> F4
    
    F3 --> F5
    F4 --> F5
    
    style P1 fill:#E81123
    style P2 fill:#E81123
    style T3 fill:#FFB900
    style F1 fill:#00BCF2
    style F2 fill:#00BCF2
    style F5 fill:#10893E
```

---

## Fluxo de Dados

```mermaid
flowchart TD
    Start([Início]) --> Auth{Autenticado<br/>Azure AD?}
    
    Auth -->|Não| Login[az login]
    Login --> Auth
    
    Auth -->|Sim| Phase1[📦 FASE 1: Setup]
    
    Phase1 --> Create1[Criar Workspace]
    Create1 --> Create2[Criar Lakehouse]
    Create2 --> Create3[Criar Pastas]
    
    Create3 --> Phase2[📁 FASE 2: Upload XMLs]
    
    Phase2 --> Upload1[employees.xml]
    Phase2 --> Upload2[hr.xml]
    Phase2 --> Upload3[wf_m_poc_xml_emp.XML]
    Phase2 --> Upload4[wf_m_poc_xml_hr.XML]
    
    Upload1 --> Phase3
    Upload2 --> Phase3
    Upload3 --> Phase3
    Upload4 --> Phase3[📓 FASE 3: Notebooks]
    
    Phase3 --> NB1[Notebook 01: Translation]
    Phase3 --> NB2[Notebook 02: Execution]
    Phase3 --> NB3[Notebook 03: Map EMP]
    Phase3 --> NB4[Notebook 04: Data Gen]
    Phase3 --> NB5[Notebook 05: Map HR]
    Phase3 --> NB6[Notebook 06: Import Guide]
    
    NB1 --> Phase4
    NB2 --> Phase4
    NB3 --> Phase4
    NB4 --> Phase4
    NB5 --> Phase4
    NB6 --> Phase4[🔄 FASE 4: Pipelines]
    
    Phase4 --> PL1[Pipeline EMP]
    Phase4 --> PL2[Pipeline HR]
    
    PL1 --> Phase5
    PL2 --> Phase5[▶️ FASE 5: Execução]
    
    Phase5 --> Exec1[Run Pipeline EMP]
    Phase5 --> Exec2[Run Pipeline HR]
    
    Exec1 --> Monitor1[Monitor Status]
    Exec2 --> Monitor2[Monitor Status]
    
    Monitor1 --> Success1{Success?}
    Monitor2 --> Success2{Success?}
    
    Success1 -->|Sim| Phase6
    Success2 -->|Sim| Phase6[✅ FASE 6: Validação]
    
    Success1 -->|Não| Error1[Log Error]
    Success2 -->|Não| Error2[Log Error]
    
    Error1 --> End
    Error2 --> End
    
    Phase6 --> Val1[Validar emp_poc.csv]
    Phase6 --> Val2[Validar hr_poc.csv]
    
    Val1 --> Check1{8 registros?}
    Val2 --> Check2{8 registros?}
    
    Check1 -->|Sim| Phase7
    Check2 -->|Sim| Phase7[📊 FASE 7: Relatório]
    
    Check1 -->|Não| Error3[Validation Failed]
    Check2 -->|Não| Error4[Validation Failed]
    
    Error3 --> End
    Error4 --> End
    
    Phase7 --> Report[Gerar migration_report.json]
    Report --> End([🎉 Concluído])
    
    style Start fill:#10893E
    style Phase1 fill:#FFB900
    style Phase2 fill:#FFB900
    style Phase3 fill:#FFB900
    style Phase4 fill:#FFB900
    style Phase5 fill:#00BCF2
    style Phase6 fill:#10893E
    style Phase7 fill:#10893E
    style End fill:#10893E
    style Error1 fill:#E81123
    style Error2 fill:#E81123
    style Error3 fill:#E81123
    style Error4 fill:#E81123
```

---

## Timeline da Migração

```mermaid
gantt
    title Migração PowerCenter → Fabric (Timeline)
    dateFormat  mm:ss
    
    section Fase 1: Setup
    Criar Workspace          :done, phase1a, 00:00, 01:00
    Criar Lakehouse          :done, phase1b, 01:00, 01:30
    Criar Pastas             :done, phase1c, 01:30, 02:00
    
    section Fase 2: Upload
    Upload XMLs (4 arquivos) :done, phase2, 02:00, 03:30
    
    section Fase 3: Notebooks
    Upload 6 Notebooks       :done, phase3, 03:30, 06:00
    
    section Fase 4: Pipelines
    Criar 2 Pipelines        :done, phase4, 06:00, 07:30
    
    section Fase 5: Execução
    Run Pipeline EMP         :active, phase5a, 07:30, 09:00
    Run Pipeline HR          :active, phase5b, 07:30, 09:30
    
    section Fase 6: Validação
    Validar Outputs          :phase6, 09:30, 10:30
    
    section Fase 7: Relatório
    Gerar Relatório          :phase7, 10:30, 11:00
```

**Duração total:** ~11 minutos

---

## Componentes Criados

```mermaid
graph TB
    subgraph WS["Workspace: PowerCenter Migration"]
        subgraph LH["Lakehouse: PowerCenterData"]
            subgraph Files["📁 Files"]
                F1[source/employees.xml]
                F2[source/hr.xml]
                F3[source/wf_m_poc_xml_emp.XML]
                F4[source/wf_m_poc_xml_hr.XML]
                F5[output/emp_poc.csv]
                F6[output/hr_poc.csv]
            end
            
            subgraph Tables["🗄️ Tables"]
                T1[emp_poc<br/>Delta Table]
                T2[hr_poc<br/>Delta Table]
            end
        end
        
        subgraph NB["📓 Notebooks"]
            N1[01_Translation]
            N2[02_Execution]
            N3[03_Map_EMP]
            N4[04_Data_Gen]
            N5[05_Map_HR]
            N6[06_Import_Guide]
        end
        
        subgraph PL["🔄 Pipelines"]
            P1[pipeline_emp_xml_to_csv]
            P2[pipeline_hr_xml_to_csv]
        end
    end
    
    F1 --> N3
    F2 --> N5
    
    N3 --> P1
    N5 --> P2
    
    P1 --> F5
    P2 --> F6
    
    F5 --> T1
    F6 --> T2
    
    style WS fill:#FFB900
    style LH fill:#00BCF2
    style NB fill:#00A4EF
    style PL fill:#8661C5
    style Files fill:#E3E3E3
    style Tables fill:#10893E
```

---

## Mapeamento de Workflows

```mermaid
graph LR
    subgraph PC["PowerCenter Workflows"]
        PC1["wf_m_poc_xml_emp<br/>├─ XML Source Qualifier<br/>├─ Expression<br/>├─ Filter<br/>└─ Target"]
        
        PC2["wf_m_poc_xml_hr<br/>├─ Hierarchical XML Parser<br/>├─ Normalizer<br/>├─ Joiner<br/>└─ Target"]
    end
    
    subgraph Fabric["Fabric Notebooks"]
        F1["03_Map_EMP<br/>├─ spark.read.xml()<br/>├─ select() + withColumn()<br/>├─ filter()<br/>└─ write.csv()"]
        
        F2["05_Map_HR<br/>├─ read_xml_hierarchical()<br/>├─ explode() + flatMap()<br/>├─ join()<br/>└─ write.csv()"]
    end
    
    PC1 -.Migração.-> F1
    PC2 -.Migração.-> F2
    
    style PC1 fill:#E81123
    style PC2 fill:#E81123
    style F1 fill:#00BCF2
    style F2 fill:#00BCF2
```

---

## Decisões de Arquitetura

| Aspecto | PowerCenter | Fabric | Justificativa |
|---------|-------------|--------|---------------|
| **Formato de dados** | XML → CSV | XML → CSV → Delta | Delta permite queries SQL e versionamento |
| **Orquestração** | Workflow Manager | Data Pipelines | Nativo do Fabric, sem infra adicional |
| **Transformação** | Mapplet | PySpark Notebook | Código versionável, testável, reutilizável |
| **Armazenamento** | File System | Lakehouse (OneLake) | Storage unificado, ACID, Delta Lake |
| **Scheduling** | pmcmd | Fabric Scheduler | Integrado, sem CLI externo |
| **Monitoramento** | Repository Manager | Azure Monitor | Observabilidade cloud-native |
| **Deploy** | Manual + Repo | MCP + Git | Automação, IaC, CI/CD |

---

## Benefícios da Migração

```mermaid
mindmap
  root((Migração<br/>PowerCenter<br/>→ Fabric))
    Custos
      TCO -60%
      Sem licenças PowerCenter
      Serverless
      Pay-per-use
    Agilidade
      Deploy < 15min
      IaC + Git
      Self-service
      No-code pipelines
    Escalabilidade
      Auto-scaling
      PySpark distribuído
      Delta Lake
      10K+ registros/seg
    Governança
      Microsoft Purview
      Lineage automático
      Role-based access
      Audit logs
    Modernização
      Cloud-native
      API-first
      MCP automation
      Notebooks interativos
```

---

## Próximos Passos

```mermaid
graph TD
    Current[Migração<br/>Concluída] --> Next1{Próximo?}
    
    Next1 -->|Produtização| Prod[🚀 Produção]
    Next1 -->|Expansão| Expand[📈 Mais Workflows]
    Next1 -->|Otimização| Opt[⚡ Performance]
    
    Prod --> Prod1[Configurar schedules]
    Prod --> Prod2[Alertas Azure Monitor]
    Prod --> Prod3[CI/CD GitHub Actions]
    
    Expand --> Exp1[Migrar mais workflows]
    Expand --> Exp2[Criar library reutilizável]
    Expand --> Exp3[Documentar padrões]
    
    Opt --> Opt1[Otimizar queries PySpark]
    Opt --> Opt2[Particionamento Delta]
    Opt --> Opt3[Caching estratégico]
    
    style Current fill:#10893E
    style Prod fill:#00BCF2
    style Expand fill:#FFB900
    style Opt fill:#8661C5
```

---

**Última atualização:** 2026-06-23  
**Ferramenta:** Mermaid.js  
**Visualização:** GitHub / VS Code / Markdown viewers
