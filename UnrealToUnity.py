import unreal
import os
import json
from datetime import datetime

class UnrealToUnityExporter:
    def __init__(self, export_path="H:/EXPORT_UNREALENGINE/"):
        # Correction du chemin pour éviter les problèmes
        self.export_path = export_path.replace("\\", "/")
        if not self.export_path.endswith("/"):
            self.export_path += "/"
        self.assets_exported = []
        
    def ensure_export_directory(self):
        """Crée le dossier d'export si il n'existe pas"""
        if not os.path.exists(self.export_path):
            os.makedirs(self.export_path)
            print(f"📁 Dossier créé: {self.export_path}")
            
    def get_assets_from_selection(self):
        """Récupère tous les assets depuis la sélection (dossiers ou assets individuels)"""
        selected_assets = []
        
        # Récupère les assets sélectionnés individuellement
        individual_assets = unreal.EditorUtilityLibrary.get_selected_assets()
        selected_assets.extend(individual_assets)
        
        # Récupère les dossiers sélectionnés via Content Browser
        selected_folders = self.get_selected_content_browser_folders()
        
        # Pour chaque dossier sélectionné, récupère tous les assets qu'il contient
        for folder_path in selected_folders:
            print(f"📂 Scan du dossier: {folder_path}")
            folder_assets = self.get_assets_in_folder(folder_path)
            selected_assets.extend(folder_assets)
        
        # Élimine les doublons
        unique_assets = []
        seen_ids = set()
        for asset in selected_assets:
            asset_id = asset.get_path_name()
            if asset_id not in seen_ids:
                unique_assets.append(asset)
                seen_ids.add(asset_id)
        
        print(f"🔍 {len(unique_assets)} assets uniques trouvés dans la sélection")
        return unique_assets
    
    def get_selected_content_browser_folders(self):
        """Récupère les dossiers sélectionnés dans le Content Browser"""
        selected_folders = []
        try:
            # Récupère la sélection du Content Browser
            content_browser = unreal.EditorUtilityLibrary.get_selected_folder_paths()
            selected_folders.extend(content_browser)
        except Exception as e:
            print(f"⚠️ Impossible de récupérer les dossiers sélectionnés: {e}")
            
        return selected_folders
    
    def get_assets_in_folder(self, folder_path):
        """Récupère tous les assets dans un dossier et ses sous-dossiers"""
        assets = []
        try:
            # Convertit le chemin du dossier en chemin d'asset
            if not folder_path.startswith("/Game/"):
                folder_path = "/Game/" + folder_path.lstrip("/")
            
            # Récupère le contenu du dossier récursivement
            asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
            asset_filter = unreal.ARFilter(
                package_paths=[folder_path],
                recursive_paths=True
            )
            asset_data_list = asset_registry.get_assets(asset_filter)
            
            for asset_data in asset_data_list:
                try:
                    asset = asset_data.get_asset()
                    if asset:
                        assets.append(asset)
                except Exception as e:
                    print(f"  ⚠️ Impossible de charger l'asset: {asset_data.object_path}")
                    
            print(f"  📁 {len(assets)} assets trouvés dans {folder_path}")
            
        except Exception as e:
            print(f"✗ Erreur scan dossier {folder_path}: {str(e)}")
        
        return assets
    
    def export_static_mesh(self, static_mesh):
        """Export un Static Mesh en FBX"""
        try:
            asset_name = static_mesh.get_name()
            filename = os.path.join(self.export_path, f"SM_{asset_name}.fbx").replace("\\", "/")
            
            export_task = unreal.AssetExportTask()
            export_task.object = static_mesh
            export_task.filename = filename
            export_task.automated = True
            export_task.replace_identical = True
            
            # Options FBX
            fbx_options = unreal.FbxExportOption()
            fbx_options.collision = False
            fbx_options.level_of_detail = False
            export_task.options = fbx_options
            
            # Exécution de l'export
            result = unreal.Exporter.run_asset_export_task(export_task)
            
            if result:
                self.assets_exported.append({
                    'type': 'StaticMesh',
                    'name': asset_name,
                    'path': filename,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"✓ Static Mesh exporté: {asset_name}")
            else:
                print(f"✗ Échec export Static Mesh: {asset_name}")
            return result
            
        except Exception as e:
            print(f"✗ Erreur export Static Mesh {static_mesh.get_name()}: {str(e)}")
            return False
    
    def export_skeletal_mesh(self, skeletal_mesh):
        """Export un Skeletal Mesh en FBX"""
        try:
            asset_name = skeletal_mesh.get_name()
            filename = os.path.join(self.export_path, f"SK_{asset_name}.fbx").replace("\\", "/")
            
            export_task = unreal.AssetExportTask()
            export_task.object = skeletal_mesh
            export_task.filename = filename
            export_task.automated = True
            export_task.replace_identical = True
            
            # Options FBX pour Skeletal Mesh
            fbx_options = unreal.FbxExportOption()
            fbx_options.lod_export_type = unreal.FbxExportLODLevel.LOD_LEVEL_ALL
            export_task.options = fbx_options
            
            result = unreal.Exporter.run_asset_export_task(export_task)
            
            if result:
                self.assets_exported.append({
                    'type': 'SkeletalMesh',
                    'name': asset_name,
                    'path': filename,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"✓ Skeletal Mesh exporté: {asset_name}")
            else:
                print(f"✗ Échec export Skeletal Mesh: {asset_name}")
            return result
            
        except Exception as e:
            print(f"✗ Erreur export Skeletal Mesh {skeletal_mesh.get_name()}: {str(e)}")
            return False
    
    def export_animation_sequence(self, anim_sequence, skeletal_mesh=None):
        """Export une Animation Sequence en FBX"""
        try:
            asset_name = anim_sequence.get_name()
            filename = os.path.join(self.export_path, f"ANIM_{asset_name}.fbx").replace("\\", "/")
            
            export_task = unreal.AssetExportTask()
            export_task.object = anim_sequence
            export_task.filename = filename
            export_task.automated = True
            
            # Options d'export d'animation
            anim_options = unreal.FbxExportOption()
            if skeletal_mesh:
                anim_options.skeletal_mesh = skeletal_mesh
            
            export_task.options = anim_options
            result = unreal.Exporter.run_asset_export_task(export_task)
            
            if result:
                self.assets_exported.append({
                    'type': 'Animation',
                    'name': asset_name,
                    'path': filename,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"✓ Animation exportée: {asset_name}")
            else:
                print(f"✗ Échec export Animation: {asset_name}")
            return result
            
        except Exception as e:
            print(f"✗ Erreur export Animation {anim_sequence.get_name()}: {str(e)}")
            return False
    
    def export_material(self, material):
        """Export un Material et ses textures"""
        try:
            asset_name = material.get_name()
            
            # Export des textures associées
            texture_exports = self.export_material_textures(material)
            
            # Création d'un fichier de description du material
            material_info = {
                'name': asset_name,
                'textures': texture_exports,
                'shader_model': 'Standard',
                'export_time': datetime.now().isoformat()
            }
            
            # Sauvegarde des infos du material
            info_filename = os.path.join(self.export_path, f"MAT_{asset_name}.json").replace("\\", "/")
            with open(info_filename, 'w') as f:
                json.dump(material_info, f, indent=2)
            
            self.assets_exported.append({
                'type': 'Material',
                'name': asset_name,
                'path': info_filename,
                'textures': texture_exports,
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"✓ Material info exporté: {asset_name}")
            return True
            
        except Exception as e:
            print(f"✗ Erreur export Material {material.get_name()}: {str(e)}")
            return False
    
    def export_material_textures(self, material):
        """Export les textures d'un material"""
        texture_exports = []
        try:
            # Récupère les textures du material
            texture_params = unreal.MaterialEditingLibrary.get_texture_parameter_names(material)
            
            for param_name in texture_params:
                texture = unreal.MaterialEditingLibrary.get_material_default_texture_parameter_value(material, param_name)
                if texture:
                    texture_path = self.export_texture(texture, param_name)
                    if texture_path:
                        texture_exports.append({
                            'parameter': param_name,
                            'path': texture_path
                        })
                        
            return texture_exports
            
        except Exception as e:
            print(f"Erreur export textures: {str(e)}")
            return texture_exports
    
    def export_texture(self, texture, suffix=""):
        """Export une texture en PNG"""
        try:
            asset_name = texture.get_name()
            filename = os.path.join(self.export_path, f"TEX_{asset_name}_{suffix}.png").replace("\\", "/")
            
            export_task = unreal.AssetExportTask()
            export_task.object = texture
            export_task.filename = filename
            export_task.automated = True
            
            result = unreal.Exporter.run_asset_export_task(export_task)
            
            if result:
                print(f"  ✓ Texture exportée: {asset_name}_{suffix}")
                return filename
            else:
                print(f"  ✗ Échec export texture: {asset_name}_{suffix}")
            return None
            
        except Exception as e:
            print(f"  ✗ Erreur export texture {texture.get_name()}: {str(e)}")
            return None
    
    def export_assets_by_class(self, assets):
        """Export les assets selon leur type"""
        stats = {
            'StaticMesh': 0,
            'SkeletalMesh': 0,
            'Animation': 0,
            'Material': 0,
            'Texture': 0,
            'Unsupported': 0
        }
        
        for asset in assets:
            asset_class = asset.get_class().get_name()
            
            if asset_class == 'StaticMesh':
                if self.export_static_mesh(asset):
                    stats['StaticMesh'] += 1
            elif asset_class == 'SkeletalMesh':
                if self.export_skeletal_mesh(asset):
                    stats['SkeletalMesh'] += 1
            elif asset_class == 'AnimSequence':
                if self.export_animation_sequence(asset):
                    stats['Animation'] += 1
            elif asset_class == 'Material':
                if self.export_material(asset):
                    stats['Material'] += 1
            elif asset_class == 'Texture2D':
                if self.export_texture(asset, "direct"):
                    stats['Texture'] += 1
            else:
                print(f"⚠️ Type non supporté: {asset_class} - {asset.get_name()}")
                stats['Unsupported'] += 1
        
        # Affiche les statistiques
        print("\n📊 Statistiques d'export:")
        for asset_type, count in stats.items():
            if count > 0:
                print(f"  {asset_type}: {count}")
    
    def export_selected(self):
        """Export les assets sélectionnés (dossiers ou assets individuels)"""
        try:
            self.ensure_export_directory()
            
            # Récupère tous les assets de la sélection
            all_assets = self.get_assets_from_selection()
            
            if not all_assets:
                print("❌ Aucun asset ou dossier sélectionné!")
                print("💡 Sélectionnez soit:")
                print("   - Des assets individuels dans le Content Browser")
                print("   - Des dossiers dans le Content Browser")
                print("   - Les deux en même temps")
                return False
            
            print(f"🚀 Début de l'export de {len(all_assets)} assets...")
            
            # Export selon le type
            self.export_assets_by_class(all_assets)
            
            # Génère un rapport d'export
            self.generate_export_report()
            
            success_count = len(self.assets_exported)
            print(f"\n✅ Export terminé! {success_count}/{len(all_assets)} assets exportés avec succès vers: {self.export_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'export: {str(e)}")
            return False
    
    def generate_export_report(self):
        """Génère un rapport d'export"""
        if not self.assets_exported:
            print("📊 Aucun asset exporté, pas de rapport généré")
            return
            
        report = {
            'export_session': {
                'timestamp': datetime.now().isoformat(),
                'total_assets': len(self.assets_exported),
                'export_path': self.export_path
            },
            'assets': self.assets_exported
        }
        
        report_filename = os.path.join(self.export_path, "export_report.json").replace("\\", "/")
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Rapport d'export généré: {report_filename}")

# 🚀 FONCTIONS D'UTILISATION SIMPLIFIÉES

def export_selected():
    """Fonction principale - Exporte la sélection actuelle"""
    exporter = UnrealToUnityExporter(export_path="H:/EXPORT_UNREALENGINE/")
    return exporter.export_selected()

def export_to_custom_path(export_path):
    """Exporte avec un chemin personnalisé"""
    exporter = UnrealToUnityExporter(export_path=export_path)
    return exporter.export_selected()

# 🎯 EXÉCUTION PRINCIPALE
def main():
    """Fonction principale - à exécuter depuis la console Python"""
    print("🚀 Démarrage de l'export Unreal to Unity...")
    success = export_selected()
    if success:
        print("🎉 Export terminé avec succès!")
    else:
        print("💥 Export échoué!")
    return success

# Exécuter le script directement
if __name__ == "__main__":
    main()