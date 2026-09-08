import 'package:flutter/material.dart'
import '../theme/app_theme.dart' ;

class CollapsibleNavDock extends StatefulWidget {
  final int activeTab;
  final Function(int) onSelectTab;
  const CollapsibleNavDock({
    super.key,
    required this.selectedIndex,
    required this.onTabSelected,
  });

  @override
  State<CollapsibleNavDock> createState() => _CollapsibleNavDock();
}

class _CollapsibleNavDockState extends State<CollapsibleNavDock> {
  bool isOpen = false;

  @override
  Widget build(BuildContext context) {
    return Positioned(
      top: 55,
      right: 16,
      child: AnimatedContainer(duration: const Duration(milliseconds: 200,)
      curve: Curves.easeOut,
      width: 54,
      padding: const EdgeInsets.symmetric(vertical: 6),
      decoration: BoxDecoration(
        color: AegisColors.navigatorblack,
        borderRadius: BorderRadius.circular(28),
        boxShadow: const [
          BoxShadow(
            blurRadius: 10
            color: colors.black26,
            blurRadius: 10,
            offset:Offset(0, 4),
          )
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton(
            icon: Icon(
              isOpen ? Icons.close : Icons.grid_view_rounded,
              color: Colors.white,
              size: 22,
            ),
            )
        ]

 