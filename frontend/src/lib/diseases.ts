export type Disease = {
  id: string;
  name: string;
  shortName: string;
  tagline: string;
  description: string;
};

export const diseases: Disease[] = [
  {
    id: "cushing",
    name: "Sindrome de Cushing",
    shortName: "Cushing",
    tagline: "Alteracion hormonal con impacto en energia, piel y peso.",
    description:
      "El sindrome de Cushing puede alterar el metabolismo y provocar cambios graduales. La herramienta ayuda a priorizar la evaluacion veterinaria.",
  },
];

export function getDiseaseById(id: string) {
  return diseases.find((disease) => disease.id === id) ?? diseases[0];
}
