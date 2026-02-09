import pandas as pd


class ExcelProcessor:
    def extract_text(self, file_path):
        pages = []
        xls = pd.ExcelFile(file_path)

        for i, sheet_name in enumerate(xls.sheet_names):
            df = pd.read_excel(xls, sheet_name=sheet_name)
            if df.empty:
                continue

            # Convert dataframe to readable text
            lines = [f"Hoja: {sheet_name}"]
            lines.append(' | '.join(str(col) for col in df.columns))
            lines.append('-' * 40)
            for _, row in df.iterrows():
                row_text = ' | '.join(str(val) for val in row.values if pd.notna(val))
                if row_text.strip():
                    lines.append(row_text)

            content = '\n'.join(lines)
            if content.strip():
                pages.append({
                    'content': content,
                    'page': i + 1,
                })

        if not pages:
            raise ValueError('No se pudo extraer texto del archivo Excel.')
        return pages
